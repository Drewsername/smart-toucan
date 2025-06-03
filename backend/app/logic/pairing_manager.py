from fastapi import HTTPException, Depends
from app.logic.base_manager import BaseManager
from app.logic.notification_manager import NotificationManager
from app.schemas.notification import NotificationCreate
import hashlib
import base64
import time


class PairingManager(BaseManager):
    def __init__(self, user_id: str):
        super().__init__(user_id)
        self.notification_manager = NotificationManager(user_id)

    def _hash_to_code(self, input_str: str) -> str:
        hash_bytes = hashlib.sha256(input_str.encode()).digest()
        short_hash = hash_bytes[:6]  # 6 bytes = 48 bits
        code_int = int.from_bytes(short_hash, 'big')
        code_base32 = base64.b32encode(code_int.to_bytes(6, byteorder='big')).decode('utf-8')
        return code_base32.replace("=", "").upper()[:6]

    async def generate_code(self) -> dict:
        await self.get_user_or_403()

        timestamp = int(time.time() * 1000)
        raw_input = f"{self.user_id}-{timestamp}"
        code = self._hash_to_code(raw_input)

        existing = await self._prisma.pairingcode.find_unique(where={"code": code})
        if existing:
            raw_input = f"{self.user_id}-{timestamp}-retry"
            code = self._hash_to_code(raw_input)

        pairing_code = await self._prisma.pairingcode.create(
            data={"userId": self.user_id, "code": code}
        )

        return self.serialize(pairing_code)

    async def use_code(self, code: str) -> dict:
        await self.get_user_or_403()

        record = await self._prisma.pairingcode.find_unique(where={"code": code})
        if not record or record.used:
            raise HTTPException(status_code=400, detail="Invalid or already used code")

        if record.userId == self.user_id:
            raise HTTPException(status_code=400, detail="Cannot pair with yourself")

        # Perform the pairing
        await self._prisma.profile.update(where={"id": self.user_id}, data={"partnerId": record.userId})
        await self._prisma.profile.update(where={"id": record.userId}, data={"partnerId": self.user_id})
        await self._prisma.pairingcode.update(where={"id": record.id}, data={"used": True})

        # Invalidate both user caches
        BaseManager.invalidate_user_cache(self.user_id)
        BaseManager.invalidate_user_cache(record.userId)

        await self.log_action("paired_with_user", {"partner_id": record.userId})
        # Notify both users
        try:
            # Notify the user who used the code
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=self.user_id,
                    type="PAIRING_SUCCESS",
                    message=f"You successfully paired with user ID {record.userId}." # Consider fetching username later
                )
            )
            # Notify the user whose code was used
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=record.userId,
                    type="PAIRING_SUCCESS",
                    message=f"User ID {self.user_id} paired with you using your code." # Consider fetching username later
                )
            )
        except Exception as e:
            print(f"Error creating pairing success notifications: {e}") # Replace with proper logging
        return {"message": "Paired successfully"}

    async def unpair(self) -> dict:
        profile = await self.get_user_or_403()

        if not profile.partnerId:
            raise HTTPException(status_code=400, detail="You are not currently paired")

        partner_id = profile.partnerId

        # Unpair both users
        await self._prisma.profile.update(where={"id": self.user_id}, data={"partnerId": None})
        await self._prisma.profile.update(where={"id": partner_id}, data={"partnerId": None})

        # Invalidate both user caches
        BaseManager.invalidate_user_cache(self.user_id)
        BaseManager.invalidate_user_cache(partner_id)

        await self.log_action("unpaired")
        # Notify the former partner
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=partner_id,
                    type="UNPAIRED",
                    message=f"User ID {self.user_id} has unpaired from you." # Consider fetching username later
                )
            )
        except Exception as e:
            print(f"Error creating unpair notification for partner {partner_id}: {e}") # Replace with proper logging
        return {"message": "Unpaired successfully"}
