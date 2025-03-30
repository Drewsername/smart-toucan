dev:
	poetry run prisma db push
	poetry run uvicorn app.main:app --reload

reset:
	poetry run prisma migrate reset

generate:
	poetry run prisma generate
