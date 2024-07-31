from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
# events.py
import asyncio
import aiohttp
from fastapi import BackgroundTasks

from app.services.event_service import EventService
from app.database import get_db

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class EventBase(BaseModel):
    businessDate: str
    eventName: str
    eventType: str
    batchOrRealtime: str
    eventTime: datetime
    eventStatus: str
    resource: str
    details: dict

class EventCreate(EventBase):
    pass

class Event(EventBase):
    eventId: str

class EventOutcome(BaseModel):
    events: List[dict]

class ChartData(BaseModel):
    eventId: str
    eventType: str
    type: str
    eventName: str
    eventKey: str
    eventStatus: str
    TimeValue: str
    outcomeStatus: str
    plotStatus: str

@router.get("/events", response_model=List[Event])
async def get_events_by_date(
    business_date: str = Query(..., alias="businessDate"),
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        events = await event_service.query_events_by_date(business_date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart_data", response_model=List[ChartData])
async def get_events_by_date_for_chart(
    business_date: str = Query(..., alias="businessDate"),
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        events = await event_service.query_events_by_date_for_chart(business_date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event_details", response_model=EventOutcome)
async def get_event_details(
    event_name: str = Query(..., alias="eventName"),
    event_status: str = Query(..., alias="eventStatus"),
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        data = await event_service.get_monthly_events(event_name, event_status)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.post("/events", response_model=Event)
async def create_event(event: EventCreate, db = Depends(get_db)):
    try:
        logger.info(f"Received event: {event.dict()}")
        event_service = EventService(db)
        event_id = f'EVT#{event.eventName}#{event.eventStatus}#{str(uuid.uuid4())}'
        event_data = event.dict()
        event_data['eventId'] = event_id
        event_data['type'] = 'event'
        event_data['timestamp'] = datetime.now().isoformat()
        logger.info(f"Processed event data: {event_data}")
        new_event = await event_service.insert_event(event_data)
        logger.info(f"Inserted event: {new_event}")
        return new_event
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/events/rabbitmq")
async def create_event_rabbitmq(event: EventCreate, db = Depends(get_db)):
    try:
        event_service = EventService(db)
        await event_service.publish_event_to_rabbitmq(event.dict())
        return {"status": "success", "message": "Event sent to RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/generate-expectations")
async def generate_expectations(
    business_date: str = Body(..., embed=True),
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        await event_service.delete_expectations_for_business_date(business_date)
        result = await event_service.generate_expectations(business_date)
        if not result:
            raise HTTPException(status_code=404, detail="Unable to generate expectations, no metrics found.")
        return {"status": "Success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/delete_events")
async def delete_events(
    business_dates: List[str] = Body(..., embed=True),
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        await event_service.delete_events_for_business_dates(business_dates)
        return {"message": "Events deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/latest-metrics", response_model=List[dict])
async def get_latest_metrics(db = Depends(get_db)):
    try:
        event_service = EventService(db)
        latest_metrics = await event_service.get_latest_metrics()
        return latest_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/expected-times/update")
async def update_expected_times(db = Depends(get_db)):
    try:
        event_service = EventService(db)
        await event_service.update_expected_times()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_name}/{event_status}/expected-time")
async def get_expected_time(
    event_name: str,
    event_status: str,
    db = Depends(get_db)
):
    try:
        event_service = EventService(db)
        expected_time = await event_service.get_expected_time(event_name, event_status)
        if not expected_time:
            raise HTTPException(status_code=404, detail="Expected time not found")
        return expected_time
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_expectation_list", response_model=List[dict])
async def get_expectation_list(db = Depends(get_db)):
    try:
        event_service = EventService(db)
        items = await event_service.get_expectation_list()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process/get_process_statistics_list", response_model=List[dict])
async def get_process_stats_list(db = Depends(get_db)):
    try:
        event_service = EventService(db)
        items = await event_service.get_process_stats_list()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))