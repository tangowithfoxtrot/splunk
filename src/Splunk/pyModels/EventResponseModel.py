from uuid import UUID
from datetime import datetime
from typing import List


class Datum:
    object: str
    type: int
    itemId: UUID
    collectionId: UUID
    groupId: UUID
    policyId: UUID
    memberId: UUID
    actingUserId: UUID
    date: datetime
    device: int
    ipAddress: str

    def __init__(
            self,
            object: str,
            type: int,
            itemId: UUID,
            collectionId: UUID,
            groupId: UUID,
            policyId: UUID,
            memberId: UUID,
            actingUserId: UUID,
            date: datetime,
            device: int,
            ipAddress: str) -> None:
        self.object = object
        self.type = type
        self.itemId = itemId
        self.collectionId = collectionId
        self.groupId = groupId
        self.policyId = policyId
        self.memberId = memberId
        self.actingUserId = actingUserId
        self.date = date
        self.device = device
        self.ipAddress = ipAddress


class EventResponseModel:
    object: str
    data: List[Datum]
    continuationToken: str

    def __init__(
            self,
            object: str,
            data: List[Datum],
            continuationToken: str = None) -> None:
        self.object = object
        self.data = data
        self.continuationToken = continuationToken
