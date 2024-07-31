import asyncio
import httpx
from datetime import datetime, timedelta
import random
import uuid
import os
import time

class Config(dict):
    def __init__(self):
        super().__init__()
        self['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO')
        self['API_URL'] = os.environ.get('API_URL', 'http://localhost:8000')
        self['CONCURRENCY_LIMIT'] = int(os.environ.get('CONCURRENCY_LIMIT', 100))
        self['BATCH_SIZE'] = int(os.environ.get('BATCH_SIZE', 50))  # New config for batch size

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

async def insert_event_batch(client, url, events):
    try:
        response = await client.post(url, json={"events": events})
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Error inserting batch: {response.text}")
            return False
    except Exception as e:
        print(f"Error inserting batch: {str(e)}")
        return False

async def insert_events(config, num_event_pairs):
    url = f"{config['API_URL']}/api/events"
    concurrency_limit = config['CONCURRENCY_LIMIT']
    batch_size = config['BATCH_SIZE']
    total_inserted = 0
    event_generator = EventGenerator()

    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(concurrency_limit)
        
        async def bounded_insert(events):
            nonlocal total_inserted
            async with semaphore:
                if await insert_event_batch(client, url, events):
                    total_inserted += len(events)

        tasks = []
        batch = []
        for _ in range(num_event_pairs):
            event_pair = event_generator.generate_event_pair()
            batch.extend(event_pair)
            if len(batch) >= batch_size:
                tasks.append(bounded_insert(batch.copy()))
                batch.clear()
        
        if batch:  # Insert any remaining events
            tasks.append(bounded_insert(batch))

        await asyncio.gather(*tasks)

    return total_inserted

async def generate_test_data(num_event_pairs: int):
    config = Config()
    
    start_time = time.time()
    
    total_inserted = await insert_events(config, num_event_pairs)
    
    total_time = time.time() - start_time
    print(f"\nTotal records inserted: {total_inserted}")
    print(f"Total event pairs inserted: {total_inserted // 2}")
    print(f"Total time elapsed: {total_time:.2f} seconds")
    print(f"Average insertion rate: {total_inserted / total_time:.2f} records/second")

async def main():
    num_event_pairs = 2000  # You can change this value or accept it as a command-line argument
    await generate_test_data(num_event_pairs)

if __name__ == "__main__":
    asyncio.run(main())
