import asyncio
import httpx
import uuid
import os
import json

class Config(dict):
    def __init__(self):
        super().__init__()
        self['API_URL'] = os.environ.get('API_URL', 'http://localhost:8000')

async def insert_event(client, url, event):
    try:
        response = await client.post(url, json=event)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        if response.status_code in [200, 201]:  # Accept both 200 and 201 as success
            print("Event inserted successfully!")
            return True
        else:
            print(f"Error inserting event. Status: {response.status_code}, Content: {response.text}")
            return False
    except Exception as e:
        print(f"Exception during event insertion: {str(e)}")
        return False

# Update the test_insert_event function as well
async def test_insert_event():
    config = Config()
    url = f"{config['API_URL']}/api/events"
    
    event = {
        'businessDate': '2024-08-01',
        'eventName': f'TestEvent_{uuid.uuid4().hex[:8]}',
        'eventType': 'TEST',
        'batchOrRealtime': 'BATCH',
        'resource': 'resource_1',
        'details': {
            'testDetail': 'This is a test detail'
        },
        'eventTime': '2024-08-01T12:00:00',
        'eventStatus': 'STARTED',
    }

    print(f"Sending request to: {url}")
    print(f"Event data: {json.dumps(event, indent=2)}")

    async with httpx.AsyncClient() as client:
        success = await insert_event(client, url, event)
        if success:
            print("Event insertion test completed successfully!")
        else:
            print("Event insertion test failed.")
            
if __name__ == "__main__":
    asyncio.run(test_insert_event())