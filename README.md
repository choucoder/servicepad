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

### Run API
1. Install postgresql
2. Create an user with username chou and password calamardo
```
$ flask db init

$ flask db migrate -m "First migration"

$ flask db upgrade

$ python3 app.py
```

### Run with Docker
1. Install docker and docker-compose and then run:
```
$ sudo docker-compose up
```
## Run Tests
```
$ pytest
```

## Changelog
- Version 1.0 : Flask API and user, publication modules