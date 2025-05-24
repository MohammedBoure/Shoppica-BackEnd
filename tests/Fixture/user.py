import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import app
from database import UserManager

user_manager = UserManager()

@pytest.fixture(autouse=True)
def setup_users():
    user_manager.clear_all_users()
    user_manager.add_user('admin', 'admin@gmail.com', 'admin', 'Admin User', '1234567890', True)
    user_manager.add_user('user2', 'user2@example.com', 'password2', 'User Two', '0987654321', False)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

API_PREFIX = '/api'

def login_and_get_token(client, email, password):
    response = client.post(f'{API_PREFIX}/login', json={
        'email': email,
        'password': password
    })
    assert response.status_code == 200
    token = response.get_json()['access_token']
    
    # احفظ التوكن في ملف بنفس المجلد
    with open(os.path.join(os.path.dirname(__file__), 'token.txt'), 'w') as f:
        f.write(token)

    return token

def test_get_user_by_id_authorized(client):
    token = login_and_get_token(client, 'admin@gmail.com', 'admin')
    admin = user_manager.get_user_by_email('admin@gmail.com')
    assert admin is not None
    user_id = admin["id"]

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'{API_PREFIX}/users/{user_id}', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'admin'

def test_get_user_by_id_unauthorized(client):
    token = login_and_get_token(client, 'user2@example.com', 'password2')
    other_user = user_manager.get_user_by_email('admin@gmail.com')
    assert other_user is not None
    user_id = other_user["id"]

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'{API_PREFIX}/users/{user_id}', headers=headers)

    assert response.status_code == 403
