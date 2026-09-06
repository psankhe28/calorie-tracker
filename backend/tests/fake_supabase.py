"""A minimal in-memory stand-in for supabase-py's query builder, covering only the
methods this app actually uses (select/insert/update/delete, eq/gte/lte, order,
range/limit, execute). Lets the test suite run fast and offline instead of hitting a
real Supabase project."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FakeResult:
    data: Any
    count: int | None = None


class FakeQuery:
    def __init__(self, table_rows: list[dict], next_id: list[int]):
        self._rows = table_rows
        self._next_id = next_id
        self._op: str | None = None
        self._payload: dict | list[dict] | None = None
        self._filters: list[tuple[str, str, Any]] = []
        self._order_field: str | None = None
        self._order_desc = False
        self._range: tuple[int, int] | None = None
        self._limit: int | None = None
        self._count_requested = False

    def select(self, *_columns: str, count: str | None = None) -> "FakeQuery":
        self._op = self._op or "select"
        if count:
            self._count_requested = True
        return self

    def insert(self, payload: dict | list[dict]) -> "FakeQuery":
        self._op = "insert"
        self._payload = payload
        return self

    def update(self, payload: dict) -> "FakeQuery":
        self._op = "update"
        self._payload = payload
        return self

    def delete(self) -> "FakeQuery":
        self._op = "delete"
        return self

    def eq(self, field_name: str, value: Any) -> "FakeQuery":
        self._filters.append(("eq", field_name, value))
        return self

    def gte(self, field_name: str, value: Any) -> "FakeQuery":
        self._filters.append(("gte", field_name, value))
        return self

    def lte(self, field_name: str, value: Any) -> "FakeQuery":
        self._filters.append(("lte", field_name, value))
        return self

    def order(self, field_name: str, desc: bool = False) -> "FakeQuery":
        self._order_field = field_name
        self._order_desc = desc
        return self

    def range(self, start: int, end: int) -> "FakeQuery":
        self._range = (start, end)
        return self

    def limit(self, n: int) -> "FakeQuery":
        self._limit = n
        return self

    def _matches(self, row: dict) -> bool:
        for op, field_name, value in self._filters:
            row_value = row.get(field_name)
            if op == "eq" and row_value != value:
                return False
            if op == "gte" and not (row_value is not None and row_value >= value):
                return False
            if op == "lte" and not (row_value is not None and row_value <= value):
                return False
        return True

    def execute(self) -> FakeResult:
        if self._op == "insert":
            payload_list = self._payload if isinstance(self._payload, list) else [self._payload]
            inserted = []
            for item in payload_list:
                row = dict(item)
                row["id"] = self._next_id[0]
                self._next_id[0] += 1
                self._rows.append(row)
                inserted.append(dict(row))
            return FakeResult(data=inserted)

        matching = [row for row in self._rows if self._matches(row)]

        if self._op == "update":
            for row in matching:
                row.update(self._payload)
            return FakeResult(data=[dict(row) for row in matching])

        if self._op == "delete":
            for row in matching:
                self._rows.remove(row)
            return FakeResult(data=[dict(row) for row in matching])

        # select
        total = len(matching)
        if self._order_field:
            matching = sorted(
                matching, key=lambda r: r.get(self._order_field), reverse=self._order_desc
            )
        if self._range:
            start, end = self._range
            matching = matching[start : end + 1]
        elif self._limit is not None:
            matching = matching[: self._limit]

        return FakeResult(data=[dict(row) for row in matching], count=total if self._count_requested else None)


class FakeTable:
    def __init__(self, rows: list[dict], next_id: list[int]):
        self._rows = rows
        self._next_id = next_id

    def select(self, *columns: str, count: str | None = None) -> FakeQuery:
        return FakeQuery(self._rows, self._next_id).select(*columns, count=count)

    def insert(self, payload: dict | list[dict]) -> FakeQuery:
        return FakeQuery(self._rows, self._next_id).insert(payload)

    def update(self, payload: dict) -> FakeQuery:
        return FakeQuery(self._rows, self._next_id).update(payload)

    def delete(self) -> FakeQuery:
        return FakeQuery(self._rows, self._next_id).delete()


@dataclass
class FakeSupabaseClient:
    _tables: dict[str, list[dict]] = field(default_factory=dict)
    _next_ids: dict[str, list[int]] = field(default_factory=dict)

    def table(self, name: str) -> FakeTable:
        rows = self._tables.setdefault(name, [])
        next_id = self._next_ids.setdefault(name, [1])
        return FakeTable(rows, next_id)
