import pytest
import os
import sys

# تعديل المسار للوصول إلى الوحدة الرئيسية
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import app  # استيراد التطبيق الرئيسي من app.py
from database import UserManager

user_manager = UserManager()
API_PREFIX = '/api'

# إعداد المستخدمين قبل الاختبارات
@pytest.fixture(autouse=True)
def setup_users():
    user_manager.clear_all_users()
    user_manager.add_user('admin', 'admin@gmail.com', 'admin', 'Admin User', '1234567890', True)
    user_manager.add_user('user2', 'user2@example.com', 'password2', 'User Two', '0987654321', False)

@pytest.fixture
def app():
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'  # المفتاح السري المحدد
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# دالة لتسجيل الدخول والحصول على توكن
def login_and_get_token(client, email, password):
    response = client.post(f'{API_PREFIX}/login', json={
        'email': email,
        'password': password
    })
    assert response.status_code == 200, f"Login failed: {response.get_json()}"
    return response.get_json()['access_token']

# توكن المسؤول
@pytest.fixture
def access_token(client):
    return login_and_get_token(client, 'admin@gmail.com', 'admin')

# توكن المستخدم العادي
@pytest.fixture
def user_token(client):
    return login_and_get_token(client, 'user2@example.com', 'password2')

# محاكاة AddressManager
@pytest.fixture(autouse=True)
def mock_address_manager(monkeypatch):
    class MockAddressManager:
        def add_address(self, user_id, address_line1, city, country, address_line2=None, state=None, postal_code=None, is_default=0):
            return 123

        def get_address_by_id(self, address_id):
            if address_id == 1:
                return {
                    'id': 1,
                    'user_id': 1,
                    'address_line1': '123 Test St',
                    'address_line2': 'Suite 100',
                    'city': 'Testville',
                    'state': 'TS',
                    'postal_code': '12345',
                    'country': 'Testland',
                    'is_default': 1
                }
            return None

        def get_addresses_by_user(self, user_id):
            if user_id == 1:
                return [self.get_address_by_id(1)]
            return []

        def update_address(self, address_id, address_line1=None, address_line2=None, city=None, state=None, postal_code=None, country=None, is_default=None):
            return address_id == 1

        def delete_address(self, address_id):
            return address_id == 1

        def get_addresses(self, page, per_page):
            addresses = [self.get_address_by_id(1)]
            total = 1
            return addresses, total

    monkeypatch.setattr('apis.addresses.address_manager', MockAddressManager())

def auth_header(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# اختبار إضافة عنوان بنجاح
def test_add_address_success(client, user_token):
    data = {
        'user_id': 1,
        'address_line1': '123 Test St',
        'city': 'Testville',
        'country': 'Testland'
    }
    response = client.post('/api/addresses', json=data, headers=auth_header(user_token))
    assert response.status_code == 201
    json_data = response.get_json()
    assert 'address_id' in json_data
    assert json_data['address_id'] == 123
    assert json_data['message'] == 'Address added successfully'

# اختبار إضافة عنوان بدون صلاحيات
def test_add_address_unauthorized(client, user_token):
    data = {
        'user_id': 2,
        'address_line1': '123 Test St',
        'city': 'Testville',
        'country': 'Testland'
    }
    response = client.post('/api/addresses', json=data, headers=auth_header(user_token))
    assert response.status_code == 403
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Unauthorized to add address for another user'

# اختبار إضافة عنوان ببيانات ناقصة
def test_add_address_missing_fields(client, user_token):
    data = {
        'user_id': 1,
        'address_line1': '123 Test St',
    }
    response = client.post('/api/addresses', json=data, headers=auth_header(user_token))
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'User ID, address line 1, city, and country are required'

# اختبار استرجاع عنوان بنجاح
def test_get_address_by_id_success(client, user_token):
    response = client.get('/api/addresses/1', headers=auth_header(user_token))
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert data['user_id'] == 1
    assert data['address_line1'] == '123 Test St'
    assert data['city'] == 'Testville'
    assert data['country'] == 'Testland'

# اختبار استرجاع عنوان غير موجود
def test_get_address_by_id_not_found(client, user_token):
    response = client.get('/api/addresses/999', headers=auth_header(user_token))
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Address not found'

# اختبار استرجاع عنوان بدون صلاحيات
def test_get_address_by_id_unauthorized(client, user_token, monkeypatch):
    def mock_get_address_by_id(address_id):
        if address_id == 2:
            return {'id': 2, 'user_id': 2, 'address_line1': '456 Other St', 'city': 'Other', 'country': 'Other', 'is_default': 0}
        return None
    import apis.addresses
    monkeypatch.setattr(apis.addresses.address_manager, 'get_address_by_id', mock_get_address_by_id)
    
    response = client.get('/api/addresses/2', headers=auth_header(user_token))
    assert response.status_code == 403
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Unauthorized access to this address'

# اختبار استرجاع عناوين المستخدم بنجاح
def test_get_addresses_by_user_success(client, user_token):
    response = client.get('/api/addresses/user/1', headers=auth_header(user_token))
    assert response.status_code == 200
    data = response.get_json()
    assert 'addresses' in data
    assert isinstance(data['addresses'], list)
    assert len(data['addresses']) == 1
    assert data['addresses'][0]['id'] == 1

# اختبار استرجاع عناوين مستخدم بدون صلاحيات
def test_get_addresses_by_user_unauthorized(client, user_token):
    response = client.get('/api/addresses/user/2', headers=auth_header(user_token))
    assert response.status_code == 403
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Unauthorized to view addresses for another user'

# اختبار تحديث عنوان بنجاح
def test_update_address_success(client, user_token):
    data = {'address_line1': '456 New St', 'city': 'Newville', 'country': 'Newland'}
    response = client.put('/api/addresses/1', json=data, headers=auth_header(user_token))
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Address updated successfully'

# اختبار تحديث عنوان غير موجود
def test_update_address_not_found(client, user_token):
    data = {'address_line1': '456 New St'}
    response = client.put('/api/addresses/999', json=data, headers=auth_header(user_token))
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Address not found'

# اختبار حذف عنوان بنجاح
def test_delete_address_success(client, user_token):
    response = client.delete('/api/addresses/1', headers=auth_header(user_token))
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Address deleted successfully'

# اختبار حذف عنوان غير موجود
def test_delete_address_not_found(client, user_token):
    response = client.delete('/api/addresses/999', headers=auth_header(user_token))
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Address not found or failed to delete'

# اختبار استرجاع جميع العناوين (للمسؤول)
def test_get_addresses_admin(client, access_token):
    response = client.get('/api/addresses?page=1&per_page=20', headers=auth_header(access_token))
    assert response.status_code == 200
    data = response.get_json()
    assert 'addresses' in data
    assert 'total' in data
    assert isinstance(data['addresses'], list)
    assert data['total'] == 1
    assert data['page'] == 1
    assert data['per_page'] == 20

# اختبار استرجاع جميع العناوين بدون صلاحيات المسؤول
def test_get_addresses_non_admin(client, user_token):
    response = client.get('/api/addresses?page=1&per_page=20', headers=auth_header(user_token))
    assert response.status_code == 403
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Admin access required'