from pydantic import BaseModel, Field
from typing import Union, Dict
from datetime import datetime

class EventDetails(BaseModel):
    fileName: Union[str, None] = None
    fileLocation: Union[str, None] = None
    fileSize: Union[int, None] = None
    numberOfRows: Union[int, None] = None
    messageId: Union[str, None] = None
    messageQueue: Union[str, None] = None
    databaseName: Union[str, None] = None
    tableName: Union[str, None] = None
    operation: Union[str, None] = None
    processName: Union[str, None] = None
    stepName: Union[str, None] = None
    status: Union[str, None] = None

class Event(BaseModel):
    businessDate: str
    eventName: str
    eventType: str
    batchOrRealtime: str
    eventTime: datetime
    eventStatus: str
    resource: str
    details: EventDetails
    eventId: str = Field(default_factory=lambda: f"EVT#{uuid.uuid4()}")

class CreateEventRequest(BaseModel):
    businessDate: str
    eventName: str
    eventType: str
    batchOrRealtime: str
    eventTime: datetime
    eventStatus: str
    resource: str
    details: Dict[str, Union[str, int]]
