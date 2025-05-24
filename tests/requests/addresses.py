import requests

BASE_URL = "http://127.0.0.1:5000/api"

def login(email=None, password=None):
    # Load token from file
    with open('tests/requests/token.txt', 'r') as f:
        token = f.read().strip()
    return token


# بيانات المسؤول
email = "admin2@example.com"
password = "strongadminpass789"
token = login(email, password)
headers = {"Authorization": f"Bearer {token}"}

if token:
    print("✅ Login successful")

    # 1. إضافة عنوان جديد
    print("\n📦 Adding address")
    response = requests.post(f"{BASE_URL}/addresses", json={
        "user_id": 1,
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "is_default": 1
    }, headers=headers)
    print(response.status_code, response.json())
    address_id = response.json().get("address_id")

    if address_id:
        # 2. استرجاع عنوان بواسطة ID
        print("\n📦 Getting address by ID")
        response = requests.get(f"{BASE_URL}/addresses/{address_id}", headers=headers)
        print(response.status_code, response.json())

        # 3. تحديث العنوان
        print("\n✏️ Updating address")
        response = requests.put(f"{BASE_URL}/addresses/{address_id}", json={
            "address_line1": "456 Updated St",
            "address_line2": "",
            "city": "Updated City",
            "state": "UP",
            "postal_code": "99999",
            "country": "Updatedland",
            "is_default": 0
        }, headers=headers)
        print(response.status_code, response.json())

        # 4. استرجاع جميع عناوين المستخدم
        print("\n📦 Getting addresses by user")
        response = requests.get(f"{BASE_URL}/addresses/user/1", headers=headers)
        print(response.status_code, response.json())

        # 5. حذف العنوان
        print("\n🗑️ Deleting address")
        response = requests.delete(f"{BASE_URL}/addresses/{address_id}", headers=headers)
        print(response.status_code, response.json())

    # 6. استرجاع جميع العناوين (مخصص للمشرف)
    print("\n📦 Getting all addresses (admin only)")
    response = requests.get(f"{BASE_URL}/addresses?page=1&per_page=5", headers=headers)
    print(response.status_code, response.json())

else:
    print("❌ Could not get token. Check credentials or server.")
