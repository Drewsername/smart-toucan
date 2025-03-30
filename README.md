# Smart Toucan - Partner Reward System

A web application that enables partners/couples to manage tasks and rewards.

## Features

1. **User Authentication & Pairing**
   - Users can sign up and log in
   - Partners can connect through a unique invitation code
   - Secure authentication powered by Supabase

2. **Task Management**
   - Create tasks for your partner to complete
   - Set point values for tasks
   - Mark tasks as completed to earn points
   - Real-time updates between partners

3. **Reward System**
   - Create rewards that can be redeemed with points
   - Redeem rewards by spending earned points
   - Track reward history

4. **Analytics**
   - View point history and balances
   - Track activity between partners
   - See completed tasks and redeemed rewards


To run backend:
`poetry run uvicorn app.main:app --reload`


## Development Principles

- ✅ **Imperative logic** with strong **object-oriented design**
- ✅ Each file < 100 lines, **single-responsibility**
- ✅ **Managers** encapsulate business logic, inheriting shared behavior
- ✅ Prisma used declaratively; Python logic kept fully **explicit & traceable**
- ✅ Easy to navigate, extend, and reason about with minimal context

---

##  Common Extensions (Database + Logic)

| Task | Checklist |
|------|----------|
| **➕ Add new table (e.g., `Wishlist`)** | 1. Add model to `schema.prisma` <br> 2. Run `poetry run prisma migrate dev --name add-wishlist` <br> 3. Run `poetry run prisma generate` |
| **🧩 Add field to existing model** | 1. Update model in `schema.prisma` <br> 2. Run `migrate dev` + `generate` |
| **📦 Add manager for new feature** | 1. Create class in `app/logic/{feature}_manager.py` inheriting `BaseManager` <br> 2. Add route in `app/api/routes/{feature}_routes.py` <br> 3. Register router in `main.py` |
| **🎯 Add new API endpoint** | 1. Add function to appropriate `*_routes.py` <br> 2. Call logic via corresponding Manager class |
| **🧪 Add new health check** | 1. Add method to `HealthCheckManager` <br> 2. Include result in `get_health_report()` |
| **🔍 Use generated Prisma client** | Use `self._prisma.model.method(...)` inside manager — all Prisma models and methods are type-safe and async-ready |

## Docker
| Command                                                                 | Description                                                  |
|------------------------------------------------------------------------|--------------------------------------------------------------|
| `docker-compose up --build`                                            | Build and start the app and database containers              |
| `docker-compose down`                                                  | Stop and remove containers                                   |
| `docker-compose exec app poetry run prisma db push`                   | Push Prisma schema to the database                           |
| `docker-compose exec app poetry run prisma studio`                    | Open Prisma Studio (GUI for DB inspection)                   |
| `docker-compose exec app bash`                                        | Open a shell inside the app container                        |
| `docker-compose exec app poetry run prisma migrate reset`             | Drop and reset the database schema (⚠️ destructive)           |
| `docker-compose exec app poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | Manually run the FastAPI app inside the container |
| `docker-compose exec app poetry run python app/seed.py`               | Run a seed script to populate the database                   |
| `docker-compose down -v && docker-compose up --build`                 | Rebuild everything and reset volumes (fresh start)           |
