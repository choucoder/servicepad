from base64 import b64encode
import json
from typing import Dict

from decouple import config
import pytest
import requests
from sqlalchemy import create_engine, delete, Table, Column, MetaData, Integer, String


meta = MetaData()

user_table = Table(
   'user', meta, 
   Column('id', Integer, primary_key = True), 
   Column('fullname', String), 
   Column('email', String), 
   Column('password', String), 
)


class TestUser:
    image = open('tests/photo.png', "rb")

    user1 = {
        'fullname': "Jose Chourio",
        'email': "jchouriopirela3@gmail.com",
        'password': "calamardo",
        'photo': b64encode(image.read()).decode('utf-8')
    }

    user2 = {
        'fullname': "Alberto Gallo",
        'email': "albertogallo@gmail.com",
        'password': "calamardo",
        'photo': b64encode(image.read()).decode('utf-8')
    }

    headers = {
        'Content-Type': 'application/json'
    }

    URL = f"http://localhost:{config('PORT')}/api/v1/users"

    def rollback_user_creation(self, email):
        engine = create_engine(config('DATABASE_URL'))
        conn = engine.connect()

        stmt = user_table.delete().where(user_table.c.email==email)
        conn.execute(stmt)

    def do_registration(self, user):
        with requests.Session() as sess:
            payload = json.dumps(user)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 201
            return resp.json()

    def do_login(self, email, password) -> Dict:
        with requests.Session() as sess:
            payload = json.dumps(
                {
                    'email': email,
                    'password': password
                }
            )
            resp = sess.post(self.URL+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 200
            return resp.json()


    def test_registration_success(self, rollback=True):
        with requests.Session() as sess:
            payload = json.dumps(self.user1)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 201
            if rollback:
                self.rollback_user_creation(self.user1['email'])


    def test_registration_wrong_photo(self):
        with requests.Session() as sess:
            user = {**self.user1}
            user['photo'] = 'Wrong photo'
            payload = json.dumps(user)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 400

    def test_registration_missing_data(self):
        with requests.Session() as sess:
            user = {
                'fullname': "Cristian Solarte"
            }
            payload = json.dumps(user)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 400
    
    def test_registrations_with_same_email(self):
        with requests.Session() as sess:
            payload = json.dumps(self.user1)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 201

            user2 = {
                'fullname': "Antonio Pirela",
                'email': self.user1['email'],
                'password': 'culebra',
                'photo': self.user1['photo']
            }
            payload = json.dumps(user2)
            resp = sess.post(self.URL, data=payload, headers=self.headers)
            assert resp.status_code == 422

            self.rollback_user_creation(user2['email'])

    
    def test_login_success(self):
        self.test_registration_success(rollback=False)
        with requests.Session() as sess:
            payload = json.dumps(
                {
                    'email': self.user1['email'],
                    'password': self.user2['password']
                }
            )
            resp = sess.post(self.URL+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 200
            self.rollback_user_creation(self.user1['email'])

    def test_login_wrong_credentials(self):
        self.test_registration_success(rollback=False)
        with requests.Session() as sess:
            payload = json.dumps(
                {
                    'email': self.user1['email'],
                    'password': 'wrongpassword'
                }
            )
            resp = sess.post(self.URL+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 401
            self.rollback_user_creation(self.user1['email'])

    def test_login_unknown_user(self):
        with requests.Session() as sess:
            payload = json.dumps(
                {
                    'email': 'user@gmail.com',
                    'password': 'mypassword'
                }
            )
            resp = sess.post(self.URL+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 401


    def test_login_wrong_schema(self):
        with requests.Session() as sess:
            payload = json.dumps(
                {
                    'name': 'user@gmail.com',
                    'passwo': 'mypassword'
                }
            )
            resp = sess.post(self.URL+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 400

    def test_user_details(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        user_id = data['id']
        token = data['token']

        with requests.Session() as sess:
            resp = sess.get(self.URL + f'/{user_id}', headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 200
        self.rollback_user_creation(user['email'])

    def test_user_details_not_found_user(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        token = data['token']

        with requests.Session() as sess:
            resp = sess.get(self.URL + '/100', headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 404
        self.rollback_user_creation(user['email'])

    def test_user_details_not_token(self):
        with requests.Session() as sess:
            resp = sess.get(self.URL + '/100', headers={
                **self.headers
            })
            assert resp.status_code == 401

    def test_user_update_success(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        token = data['token']
        user_id = data['id']

        user['fullname'] = "Jose Antonio Chourip"
        user['password'] = "calamard"
        user['photo'] = user['photo']
        user['email'] = "newemail@gmail.com"

        payload = json.dumps(user)

        with requests.Session() as sess:
            resp = sess.put(self.URL + f'/{user_id}', data=payload, headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 200

        self.rollback_user_creation(user['email'])


    def test_user_partial_update_success(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        token = data['token']
        user_id = data['id']

        user['fullname'] = "Jose Antonio Chourio"
        user['password'] = "calamar"

        payload = json.dumps(user)

        with requests.Session() as sess:
            resp = sess.patch(self.URL + f'/{user_id}', data=payload, headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 200

        self.rollback_user_creation(user['email'])


    def test_user_delete_success(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        token = data['token']
        user_id = data['id']

        with requests.Session() as sess:
            resp = sess.delete(self.URL + f'/{user_id}', headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 204

    def test_user_list_all(self):
        user = self.user1
        self.do_registration(user)
        data = self.do_login(user['email'], user['password'])
        token = data['token']

        with requests.Session() as sess:
            resp = sess.get(self.URL, headers={
                **self.headers, 'x-access-token': token
            })
            assert resp.status_code == 200
            assert isinstance(resp.json()['data'], list)
        self.rollback_user_creation(user['email'])