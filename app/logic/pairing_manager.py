from fastapi import HTTPException
from app.logic.base_manager import BaseManager
import hashlib
import base64
import time


class PairingManager(BaseManager):
    def __init__(self, user_id: str):
        super().__init__(user_id)

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
        return {"message": "Unpaired successfully"}
