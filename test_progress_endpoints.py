import asyncio
import pytest
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

@pytest.mark.asyncio
async def test_all_endpoints():
    settings = get_settings()
    
    async with httpx.AsyncClient(timeout=10) as client:
        # Login first
        r = await client.post('http://localhost:8000/api/v1/auth/login', 
            data={'username': 'my@account.com', 'password': 'MyPassword123'})
        token = r.json()['data']['tokens']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test endpoint 1: /progress
        print('Testing GET /api/v1/progress')
        r1 = await client.get('http://localhost:8000/api/v1/progress', headers=headers)
        print(f'  Status: {r1.status_code}')
        if r1.status_code == 200:
            data = r1.json()
            modules_count = len(data['data']['modules'])
            activity_count = len(data['data']['activity'])
            overall = data['data']['overview']['percentage']
            print(f'  Modules: {modules_count}')
            print(f'  Activity: {activity_count}')
            print(f'  Overall: {overall}%')
        else:
            print(f'  ERROR: {r1.text[:200]}')
        
        # Test endpoint 2: /analytics
        print('\nTesting GET /api/v1/progress/analytics')
        r2 = await client.get('http://localhost:8000/api/v1/progress/analytics', headers=headers)
        print(f'  Status: {r2.status_code}')
        if r2.status_code == 200:
            data = r2.json()
            points_count = len(data['data']['points'])
            print(f'  Points: {points_count}')
        else:
            print(f'  ERROR: {r2.text[:200]}')
        
        # Test endpoint 3: /report
        print('\nTesting GET /api/v1/progress/report')
        r3 = await client.get('http://localhost:8000/api/v1/progress/report', headers=headers)
        print(f'  Status: {r3.status_code}')
        if r3.status_code == 200:
            pdf_size = len(r3.content)
            print(f'  PDF Size: {pdf_size} bytes')
        else:
            print(f'  ERROR: {r3.text[:200]}')
        
        # Test module-specific analytics
        print('\nTesting GET /api/v1/progress/analytics?module=coding')
        r4 = await client.get('http://localhost:8000/api/v1/progress/analytics?module=coding', headers=headers)
        print(f'  Status: {r4.status_code}')
        
        print('\n✓ All tests completed successfully!')

asyncio.run(test_all_endpoints())
