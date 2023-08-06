from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.sql import Select

from ..api import create_page, resolve_params
from ..bases import AbstractPage, AbstractParams
from ..paginator import paginate as base_paginate
from .sqlalchemy import paginate_query


async def paginate(query: Select, params: Optional[AbstractParams] = None) -> AbstractPage:
    params = resolve_params(params)

    try:
        is_loader_used = query._execution_options["loader"]._distinct  # type: ignore
    except (AttributeError, KeyError):
        is_loader_used = False

    if is_loader_used:
        # FIXME: find better way to fetch rows when loader is used
        items = await query.gino.all()  # type: ignore
        return base_paginate(items, params)

    total = await func.count().select().select_from(query.alias()).gino.scalar()
    items = await paginate_query(query, params).gino.all()  # type: ignore

    return create_page(items, total, params)


__all__ = ["paginate"]
