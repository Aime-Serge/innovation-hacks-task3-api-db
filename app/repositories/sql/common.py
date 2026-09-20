"""Helpers shared by the SQL repositories: escaping, ordering, pagination, guarded execution."""

import asyncio
from collections.abc import Callable, Sequence
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, Select, SQLColumnExpression, collate, func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ServiceUnavailable
from app.domain.queries import Page
from app.repositories.sql.errors import Operation, translate

TOTAL = "_total"
BATCH = 5000


def like_pattern(term: str | None) -> str | None:
    """BR-308: `%`, `_` and `\\` in a search term match themselves; blank means no filter."""
    needle = (term or "").strip()
    if needle == "":
        return None
    escaped = needle.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def codepoint_order(expression: SQLColumnExpression[str]) -> SQLColumnExpression[str]:
    """Order text by code point, as the in-memory backend does, whatever the database locale."""
    return cast("SQLColumnExpression[str]", collate(expression, "C"))


async def run(
    session: AsyncSession, statement: Executable, operation: Operation
) -> CursorResult[Any]:
    """Execute a statement; a database failure becomes the API error for that operation."""
    try:
        async with asyncio.timeout(session.info.get("timeout")):
            return cast("CursorResult[Any]", await session.execute(statement))
    except TimeoutError:
        # The server stopped answering: drop the connection instead of waiting on it again, so a
        # dead database is reported within seconds and never holds a request open (NFR-312).
        await session.invalidate()
        raise ServiceUnavailable("A dependency is not ready.") from None
    except DBAPIError as error:
        mapped = translate(error, operation)
        if mapped is None:
            raise
        raise mapped from None


async def run_many(
    session: AsyncSession, statement: Executable, rows: Sequence[dict[str, Any]]
) -> None:
    """Bulk insert in batches, for seeding (FR-321)."""
    for start in range(0, len(rows), BATCH):
        try:
            await session.execute(statement, list(rows[start : start + BATCH]))
        except DBAPIError as error:
            mapped = translate(error, "insert")
            if mapped is None:
                raise
            raise mapped from None


async def page_of[T](
    session: AsyncSession,
    statement: Select[Any],
    count_source: Select[Any],
    page: int,
    page_size: int,
    build: Callable[[Any], T],
) -> Page[T]:
    """One query returns the rows and the total (a window count), so a list costs one query.

    Only a page past the end has no row to carry the total, and then a count query is used.
    """
    paged = statement.add_columns(func.count().over().label(TOTAL))
    result = await run(session, paged.limit(page_size).offset((page - 1) * page_size), "read")
    rows = result.all()
    if rows:
        return Page([build(row) for row in rows], page, page_size, int(getattr(rows[0], TOTAL)))
    if page == 1:
        return Page([], page, page_size, 0)
    counted = await run(session, select(func.count()).select_from(count_source.subquery()), "read")
    return Page([], page, page_size, int(counted.scalar_one()))
