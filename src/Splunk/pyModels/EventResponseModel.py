from uuid import UUID
from datetime import datetime
from typing import List


class Datum:
    object: str
    type: int
    item_id: UUID
    collection_id: UUID
    group_id: UUID
    policy_id: UUID
    member_id: UUID
    acting_user_id: UUID
    date: datetime
    device: int
    ip_address: str

    def __init__(
            self,
            object: str,
            type: int,
            item_id: UUID,
            collection_id: UUID,
            group_id: UUID,
            policy_id: UUID,
            member_id: UUID,
            acting_user_id: UUID,
            date: datetime,
            device: int,
            ip_address: str) -> None:
        self.object = object
        self.type = type
        self.item_id = item_id
        self.collection_id = collection_id
        self.group_id = group_id
        self.policy_id = policy_id
        self.member_id = member_id
        self.acting_user_id = acting_user_id
        self.date = date
        self.device = device
        self.ip_address = ip_address


class EventResponseModel:
    object: str
    data: List[Datum]

    def __init__(self, object: str, data: List[Datum]) -> None:
        self.object = object
        self.data = data
