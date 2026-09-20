"""Operator-only helpers that are not part of the repository contract (seed reset, FR-321)."""

from sqlalchemy import text

from app.repositories.sql.session import Database

# Children first, so no foreign key ever objects. The application role may DELETE, not TRUNCATE.
_TABLES = ("activity", "tasks", "projects", "users")


async def clear_all(database: Database) -> None:
    async with database.engine.begin() as connection:
        for table in _TABLES:
            await connection.execute(text(f"DELETE FROM {table}"))  # noqa: S608 - fixed names
