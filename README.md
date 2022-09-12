# Flask API test

Backend knowledge application test, API Rest

## Installation
First, clone the repository
```
$ git clone https://github.com/choucoder/servicepad.git
```

### Installation non-docker version
#### Postgresql installation and configure
```
$ sudo apt install postgresql postgresql-contrib

$ sudo su postgres

$ psql

$ postgres=# \c postgres;

$ postgres=# CREATE USER chou WITH PASSWORD 'calamardo';

$ postgres=# GRANT ALL PRIVILEGES ON DATABASE postgres TO chou;

$ postgres=# exit;
```
#### Required libraries
```
$ cd servicepad

$ sudo apt install python3-venv

$ python3 -m venv .venv

$ source .venv/bin/activate

$ python3 -m pip install -r requirements.txt
```

### Installation with Docker
```
$ sudo apt install docker container-io docker-compose
```


## Run Flask API

### Run API non-docker
```
$ flask db init

$ flask db migrate -m "First migration"

$ flask db upgrade

$ python3 app.py
```

### Run API with Docker
```
$ sudo docker-compose up
```

## Run Tests
```
$ pytest
```

## Swagger test
- http://0.0.0.0:8000/apidocs

## Changelog
- Version 1.0 : Flask API and user, publication modules