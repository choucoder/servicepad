# Flask API test

Backend knowledge application test, API Rest

## Installation
### Install postgresql
```
$ sudo apt install postgresql postgresql-contrib
```
### Install required libraries
```
$ python3 -m pip install -r requirements.txt
```

## Run Flask API
Run migrations
```
$ flask db init

$ flask db migrate -m "First migration"

$ flask db upgrade

```
### Run API
```
$ python3 app.py
```

### Run with Docker
In the .env file, change the DATABASE_URL host from 0.0.0.0 to DB, Then: 
```
$ sudo docker-compose up
```
## Run Tests
```
$ pytest
```

## Changelog
- Version 1.0 : Flask API and user, publication modules