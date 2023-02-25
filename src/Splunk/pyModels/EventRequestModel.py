from uuid import UUID
from datetime import datetime
from typing import List


class Datum:
    object: str
    start: datetime
    end: datetime
    acting_user_id: UUID
    item_id: UUID

    def __init__(
            self,
            object: str,
            start: datetime,
            end: datetime,
            acting_user_id: UUID,
            item_id: UUID) -> None:
        self.object = object
        self.start = start
        self.end = end
        self.acting_user_id = acting_user_id
        self.item_id = item_id


class EventResponseModel:
    object: str
    data: List[Datum]

    def __init__(self, object: str, data: List[Datum]) -> None:
        self.object = object
        self.data = data
