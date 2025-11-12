import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from passlib.hash import bcrypt

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users')

class UserDB:

    @staticmethod
    def create_user(email, username, password, is_superuser=False, first_name='', last_name=''):
        hashed_pw = bcrypt.hash(password)
        item = {
            'email': email,
            'username': username,
            'password_hash': hashed_pw,
            'is_superuser': is_superuser,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
        return item

    @staticmethod
    def get_user(email):
        response = table.get_item(Key={'email': email})
        return response.get('Item')

    @staticmethod
    def authenticate(email, password):
        user = UserDB.get_user(email)
        if not user:
            return None
        if bcrypt.verify(password, user['password_hash']):
            return user
        return None

    @staticmethod
    def all_users():
        return table.scan().get('Items', [])
