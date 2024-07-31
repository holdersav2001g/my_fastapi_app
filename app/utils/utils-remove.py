# utils.py
import random
import uuid
from datetime import datetime, timedelta
from app.models.models import Event, EventDetails
from .utils import EventGenerator, Config

class EventGenerator:
    def __init__(self):
        self.event_counter = 0
        self.generated_events = set()

    def generate_event_pair(self):
        event_types = ['FILE', 'MESSAGE', 'DATABASE', 'PROCESS']
        
        while True:
            self.event_counter += 1
            business_date = (datetime.now() + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
            event_type = random.choice(event_types)
            event_name = f'TestEvent_{self.event_counter:04d}'
            
            event_key = (business_date, event_name, event_type)
            if event_key not in self.generated_events:
                self.generated_events.add(event_key)
                break

        details = {}
        if event_type == 'FILE':
            details = {
                'fileName': f'file_{uuid.uuid4().hex[:8]}.txt',
                'fileLocation': f'/path/to/{uuid.uuid4().hex[:8]}',
                'fileSize': random.randint(1000, 1000000),
                'numberOfRows': random.randint(10, 10000)
            }
        elif event_type == 'MESSAGE':
            details = {
                'messageId': uuid.uuid4().hex,
                'messageQueue': f'queue_{random.randint(1, 10)}'
            }
        elif event_type == 'DATABASE':
            details = {
                'databaseName': f'db_{random.randint(1, 5)}',
                'tableName': f'table_{random.randint(1, 20)}',
                'operation': random.choice(['INSERT', 'UPDATE', 'DELETE', 'SELECT'])
            }
        elif event_type == 'PROCESS':
            details = {
                'processName': f'process_{random.randint(1, 10)}',
                'stepName': f'step_{random.randint(1, 5)}',
                'status': 'COMPLETED'
            }
        
        start_time = datetime.strptime(business_date, '%Y-%m-%d') + timedelta(minutes=random.randint(0, 1380))  # Up to 23 hours
        end_time = start_time + timedelta(minutes=random.randint(5, 60))  # 5 to 60 minutes later
        
        base_event = {
            'businessDate': business_date,
            'eventName': event_name,
            'eventType': event_type,
            'batchOrRealtime': random.choice(['BATCH', 'REALTIME']),
            'resource': f'resource_{random.randint(1, 10)}',
            'details': details
        }
        
        started_event = base_event.copy()
        started_event.update({
            'eventTime': start_time.isoformat(),
            'eventStatus': 'STARTED',
            'eventId': f"EVT#{event_name}#STARTED#{uuid.uuid4()}"
        })
        
        success_event = base_event.copy()
        success_event.update({
            'eventTime': end_time.isoformat(),
            'eventStatus': 'SUCCESS',
            'eventId': f"EVT#{event_name}#SUCCESS#{uuid.uuid4()}"
        })
        
        return [started_event, success_event]
