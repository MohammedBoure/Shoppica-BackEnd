import requests

BASE_URL = 'http://localhost:5000/api'

# Load token from file
with open('tests/requests/token.txt', 'r') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

def test_get_user_by_id(user_id):
    url = f"{BASE_URL}/users/{user_id}"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    print('GET /users/<id>:', response.status_code)
    print('Response text:', response.text)
    try:
        print('JSON:', response.json())
    except Exception as e:
        print('Failed to parse JSON:', e)


def test_get_user_by_email(email):
    response = requests.get(f'{BASE_URL}/users/email/{email}', headers=headers)
    print('GET /users/email/<email>:', response.status_code, response.json())

def test_get_user_by_username(username):
    response = requests.get(f'{BASE_URL}/users/username/{username}', headers=headers)
    print('GET /users/username/<username>:', response.status_code, response.json())

def test_update_user(user_id):
    payload = {
        'full_name': 'Updated Name',
        'phone_number': '9999999999',
        'password': 'newpassword123'
    }
    response = requests.put(f'{BASE_URL}/users/{user_id}', headers=headers, json=payload)
    print('PUT /users/<id>:', response.status_code, response.json())

def test_validate_password(user_id, password):
    payload = {'password': password}
    response = requests.post(f'{BASE_URL}/users/{user_id}/validate-password', headers=headers, json=payload)
    print('POST /users/<id>/validate-password:', response.status_code, response.json())

def test_get_users():
    response = requests.get(f'{BASE_URL}/users?page=1&per_page=10', headers=headers)
    print('GET /users:', response.status_code)
    try:
        print(response.json())
    except Exception:
        print("Invalid JSON response")

def test_delete_user(user_id):
    response = requests.delete(f'{BASE_URL}/users/{user_id}', headers=headers)
    print('DELETE /users/<id>:', response.status_code, response.json())


# ------------ Execute Tests ------------
USER_ID = 1  # Put actual test user ID here
EMAIL = "admin2@example.com"
USERNAME = "adminuser2"
PASSWORD = "strongadminpass789"

print("\n--- Running API Tests ---\n")
test_get_user_by_id(USER_ID)
test_get_user_by_email(EMAIL)
test_get_user_by_username(USERNAME)
test_update_user(USER_ID)
test_validate_password(USER_ID, PASSWORD)
test_get_users()
# test_delete_user(USER_ID)  # Uncomment carefully!
