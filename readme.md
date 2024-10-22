## FastAPI with FastAPI-users and dynamodb

For those who are working with fastapi and dynamodb as database. Also integrated fastapi-user package for handling authentication 

### Run Project

```
uvicorn app.main:app --reload
```

## Requirements: 

fastapi-users fastapi uvicorn pynamodb passlib python-decouple

### requirements.txt
```
fastapi==0.115.2
fastapi-users==13.0.0
passlib==1.7.4
pynamodb==6.0.1
python-decouple==3.8
uvicorn==0.32.0
```

## Authentication work flow

1. Access token updated on user document upon login
2. Access token removed on logout
3. Custom function named JWTDBAuthentication for Authorization 

## Sample .env

```
AWS_REGION='us-east-1'
DATABASE_HOST='http://localhost:8000'
ENVIRONMENT='local'
```

## Folder structure

```
your_project/
    └── app/
        ├── main.py
        ├── models.py
        ├── schemas.py
        ├── auth.py
        ├── managers.py
        ├── routes.py
        └── dependencies.py
```