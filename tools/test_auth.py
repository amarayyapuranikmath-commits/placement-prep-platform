import requests

BASE = 'http://127.0.0.1:8000/api/v1/auth'

reg_payload = {
    'full_name': 'Test User',
    'email': 'test@example.com',
    'password': 'Password1!'
}
print('Registering...')
r = requests.post(f'{BASE}/register', json=reg_payload)
print('REGISTER', r.status_code, r.text)

print('\nLogging in...')
login = requests.post(f'{BASE}/login', data={'username': reg_payload['email'], 'password': reg_payload['password']})
print('LOGIN', login.status_code, login.text)

print('\nAttempting login with OAuth form encoding explicitly...')
login2 = requests.post(f'{BASE}/login', data={'username': reg_payload['email'], 'password': reg_payload['password'], 'grant_type': 'password'})
print('LOGIN2', login2.status_code, login2.text)
