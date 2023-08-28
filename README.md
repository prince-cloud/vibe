## VIBE APP API

## 🚀 Features Includes

1. User Authentication and Profiles
2. Content Creation and Interaction
3. Following and Followers
4. Groups and Communities
5. Commenting and Replies
6. Search and Discovery
7. Privacy and Security
8. API Documentation and Testing

---

## 📖 Installation
To start, clone the repo to your local computer and change into the proper directory.

```
$ git clone https://github.com/prince-cloud/vibe.git
$ cd vibe
```

### Pip

```
$ python -m venv .venv

# Windows, on terminal
$ call .venv\Scripts\Activate.ps1

# macOS
$ source .venv/bin/activate

(.venv) $ pip install -r requirements.txt
(.venv) $ python manage.py migrate
(.venv) $ python manage.py createsuperuser
(.venv) $ python manage.py runserver

# Load the site at http://127.0.0.1:8000
# Load the Read Docs at http://127.0.0.1:8000/api/schema/redoc/
```

## Common endpoints

---
```
#login
# Login can be done with username, phone_number or email
# with the password combination.
/auth/v1/token/

#sign up
/auth/v1/register/

#activate account
/auth/v1/register/activate/

#resend OTP
/auth/v1/register/resend-otp/

#post
/post/v1/posts/

#community
/auth/v1/register/resend-otp/

#groups
/community/v1/groups/
```
---



[The MIT License](LICENSE)
