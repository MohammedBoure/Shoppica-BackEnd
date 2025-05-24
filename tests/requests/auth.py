import requests

# معلومات المستخدم لتسجيل الدخول
credentials = {
    "email": "admin@gmail.com",
    "password": "admin"
}

# عنوان الـ API (تأكد من أنه يتطابق مع خادمك)
url = "http://127.0.0.1:5000/api/login"

# إرسال الطلب
response = requests.post(url, json=credentials)

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")

    if token:
        with open("tests/requests/token.txt", "w") as f:
            f.write(token)
        print("Token saved to token.txt")
    else:
        print("Login succeeded, but no token found in response.")
else:
    print(f"Login failed: {response.status_code} - {response.text}")
