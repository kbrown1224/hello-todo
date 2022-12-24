"""Card Database Model"""
import pendulum
from ormar import DateTime, Integer, String, Text
from ormar import Enum as OrmarEnum
from enum import Enum

from api.bases import PydanticBaseModel
from api.bases import OrmarBaseModel

from api.database import database, metadata
from typing import Self, Any
from rich.repr import RichReprResult


class State(str, Enum):
    IN_PROGRESS = 'In Progress'
    TODO = 'ToDo'
    DONE = 'Done'

    def __lt__(self, other: Self):
        order_map = {
            self.IN_PROGRESS: 1,
            self.TODO: 2,
            self.DONE: 3
        }
        return order_map[self] < order_map[other]


class Priority(str, Enum):
    URGENT = 'Urgent'
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'

    def __lt__(self, other: Self):
        order_map = {
            self.URGENT: 1,
            self.HIGH: 2,
            self.MEDIUM: 3,
            self.LOW: 4
        }
        return order_map[self] < order_map[other]


class Card(OrmarBaseModel):
    """Card Model"""

    class Meta:
        database = database
        metadata = metadata
        tablename = "cards"

    id: int = Integer(primary_key=True)
    title: str = String(max_length=100, nullable=False)
    summary: str | None = Text(nullable=True)
    state: State = OrmarEnum(default=State.TODO, nullable=False, enum_class=State)
    priority: Priority = OrmarEnum(default=Priority.LOW, nullable=False, enum_class=Priority)
    created_dttm: pendulum.DateTime = DateTime(default=pendulum.now)
    started_dttm: pendulum.DateTime | None = DateTime(nullable=True)
    finished_dttm: pendulum.DateTime | None = DateTime(nullable=True)


class CardCreate(PydanticBaseModel):
    title: str
    summary: str | None
    state: State = State.TODO
    priority: Priority = Priority.LOW


class CardUpdate(PydanticBaseModel):
    title: str | None
    summary: str | None
    priority: Priority | None


class CardRead(PydanticBaseModel):
    id: int
    title: str
    summary: str | None
    state: State
    priority: Priority
    created_dttm: pendulum.DateTime
    started_dttm: pendulum.DateTime | None
    finished_dttm: pendulum.DateTime | None

    def __repr__(self):
        return f"<Card {self.id} - {self.state.name}>"

    def __rich_repr__(self) -> RichReprResult:
        yield self.id
        yield "state", self.state.name
        yield "priority", self.priority.name
        yield "..."


class Operator(str, Enum):
    LESS_THAN = '<'
    GREATER_THAN = '>'
    IN = 'in'


class Filter(PydanticBaseModel):
    field: str
    operator: Operator
    value: Any


class FilteredCards(PydanticBaseModel):
    offset: int
    filters: list[Filter]
    cards: list[CardRead]
