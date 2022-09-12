# Flask API test

Backend knowledge application test, API Rest

## Installation
```
$ python3 -m pip install -r requirements.txt
```

## Run Flask API
### Run migrations
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
```
$ docker build -t flask-example .

$ docker run -p 5000:5000 --name flask-example flask-example 

```
## Run Tests
```
$ pytest
```

## Changelog
- Version 1.0 : Flask API and user, publication modules