from base64 import b64encode
import json
import random
from typing import Dict

from decouple import config
import pytest
import requests
from sqlalchemy import create_engine, delete, Table, Column, MetaData, Integer, String, DateTime


meta = MetaData()

publication_table = Table(
   'publication_table', meta, 
   Column('id', Integer, primary_key = True), 
   Column('title', String), 
   Column('description', String), 
   Column('priority', String), 
   Column('status', String),
   Column('user_id', Integer),
   Column('created_at', DateTime),
   Column('updated_at', DateTime),
)

user_table = Table(
   'user', meta, 
   Column('id', Integer, primary_key = True), 
   Column('fullname', String), 
   Column('email', String), 
   Column('password', String), 
)

class TestPublication:
    url = f'http://localhost:{config("PORT")}/api/v1/publications'

    headers = {
        'Content-Type': 'application/json'
    }
    image = open('tests/photo.png', "rb")

    user = {
        'email': 'joticachourio.integral@gmail.com',
        'photo': b64encode(image.read()).decode('utf-8'),
        'fullname': 'Jose Chourio',
        'password': 'calamardo'
    }

    user2 = {
        'email': 'marcosssalonso@gmail.com',
        'photo': user['photo'],
        'fullname': 'Marcos Alonso',
        'password': 'calamardo'
    }

    post = {
        'title': "Post title jajaja",
        'description': f"Post descriptionss{random.randint(0, 100000)}",
        'priority': "NORMAL",
        'status': "1"
    }
    
    def rollback_user_creation(self, id):
        engine = create_engine(config('DATABASE_URL'))
        conn = engine.connect()
        stmt = user_table.delete().where(user_table.c.id==id)
        conn.execute(stmt)

    def rollback_post_creation(self, id):
        engine = create_engine(config('DATABASE_URL'))
        conn = engine.connect()
        stmt = publication_table.delete().where(publication_table.c.id==id)
        conn.execute(stmt)

    def create_and_get_token(self, user):
        url = f"http://localhost:{config('PORT')}/api/v1/users"

        with requests.Session() as sess:
            payload = json.dumps(user)
            resp = sess.post(url, data=payload, headers=self.headers)
            assert resp.status_code == 201

            payload = json.dumps(
                {
                    'email': user['email'],
                    'password': user['password']
                }
            )
            resp = sess.post(url+'/login', data=payload, headers=self.headers)
            assert resp.status_code == 200
            return resp.json()

    def test_publication_create_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post_id = resp.json()['data']['id']

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    
    def test_publication_update_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'title': "First post updated",
                'description': "This post has been updated from here",
                'priority': "URGENT",
                'status': "1"
            }
            payload = json.dumps(post)

            resp = sess.put(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 200

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_partial_update_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'priority': "URGENT",
            }
            payload = json.dumps(post)

            resp = sess.patch(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 200

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    
    def test_publication_delete_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            resp = sess.delete(self.url + f'/{post_id}', headers=headers)
            assert resp.status_code == 204

        self.rollback_user_creation(user)

    def test_publication_details_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            resp = sess.get(self.url + f'/{post_id}', headers=headers)
            assert resp.status_code == 200

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_list_success(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.get(self.url, headers=headers)
            assert resp.status_code == 200
            assert isinstance(resp.json()['data'], list)

        self.rollback_user_creation(user)


    def test_publication_create_wrong_schema(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            post = {
                'titl': '1',
                'description': 'This is a post description',
                'priority': 'NORMAL',
                'status': '1'
            }
            payload = json.dumps(post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 400

        self.rollback_user_creation(user)

    def test_publication_create_missing_token(self):
        with requests.Session() as sess:
            payload = json.dumps(self.post)
            resp = sess.post(self.url, data=payload, headers=self.headers)
            assert resp.status_code == 401


    def test_publication_update_wrong_schema(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'description': "This post has been updated from here",
                'priority': "URGENT",
                'status': "1"
            }
            payload = json.dumps(post)

            resp = sess.put(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 400

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_update_missing_token(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'title': "This is my second title",
                'description': "This post has been updated from here",
                'priority': "URGENT",
                'status': "1"
            }
            payload = json.dumps(post)

            resp = sess.put(self.url + f'/{post_id}', data=payload, headers=self.headers)
            assert resp.status_code == 401

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_update_unauthorized_user(self):
        data_1 = self.create_and_get_token(self.user)
        data_2 = self.create_and_get_token(self.user2)

        user_1 = data_1['id']
        user_2 = data_2['id']

        with requests.Session() as sess:
            # Create a post for user 1
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data_1['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201

            post = resp.json()['data']
            post_id = post['id']

            # User 2 is going to try to update the post
            post = {
                'title': "This is my second title",
                'description': "This post has been updated from here",
                'priority': "URGENT",
                'status': "1"
            }
            payload = json.dumps(post)
            headers['x-access-token'] = data_2['token']
            resp = sess.put(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 403

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user_2)
        self.rollback_user_creation(user_1)


    def test_publication_partial_update_wrong_schema(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'prioriti': "URGENT"
            }
            payload = json.dumps(post)

            resp = sess.patch(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 400

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_partial_update_missing_token(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            post = {
                'status': "1"
            }
            payload = json.dumps(post)

            resp = sess.patch(self.url + f'/{post_id}', data=payload, headers=self.headers)
            assert resp.status_code == 401

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_partial_update_unauthorized_user(self):
        data_1 = self.create_and_get_token(self.user)
        data_2 = self.create_and_get_token(self.user2)

        user_1 = data_1['id']
        user_2 = data_2['id']

        with requests.Session() as sess:
            # Create a post for user 1
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data_1['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201

            post = resp.json()['data']
            post_id = post['id']

            # User 2 is going to try to update the post
            post = {
                'status': "1"
            }
            payload = json.dumps(post)
            headers['x-access-token'] = data_2['token']
            resp = sess.patch(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 403

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user_2)
        self.rollback_user_creation(user_1)


    def test_publication_delete_unauthorized_user(self):
        data_1 = self.create_and_get_token(self.user)
        data_2 = self.create_and_get_token(self.user2)

        user_1 = data_1['id']
        user_2 = data_2['id']

        with requests.Session() as sess:
            # Create a post for user 1
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data_1['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201

            post = resp.json()['data']
            post_id = post['id']

            # User 2 is going to try to delete the post
            payload = json.dumps(post)
            headers['x-access-token'] = data_2['token']
            resp = sess.delete(self.url + f'/{post_id}', data=payload, headers=headers)
            assert resp.status_code == 403

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user_2)
        self.rollback_user_creation(user_1)


    def test_publication_details_missing_token(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            payload = json.dumps(self.post)
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.post(self.url, data=payload, headers=headers)
            assert resp.status_code == 201
            post = resp.json()['data']
            post_id = post['id']

            resp = sess.get(self.url + f'/{post_id}', headers=self.headers)
            assert resp.status_code == 401

        self.rollback_post_creation(post_id)
        self.rollback_user_creation(user)

    def test_publication_list_missing_token(self):
        data = self.create_and_get_token(self.user)
        user = data['id']
        with requests.Session() as sess:
            resp = sess.get(self.url, headers=self.headers)
            assert resp.status_code == 401
        self.rollback_user_creation(user)

    def test_publication_details_not_found(self):
        data = self.create_and_get_token(self.user)
        user = data['id']

        with requests.Session() as sess:
            headers = {**self.headers, 'x-access-token': data['token']}
            resp = sess.get(self.url + f'/100', headers=headers)
            assert resp.status_code == 404
        self.rollback_user_creation(user)