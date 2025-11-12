import boto3
from datetime import datetime
from django.conf import settings
import hashlib

# DynamoDB Users table
dynamodb = boto3.resource('dynamodb', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
users_table = dynamodb.Table('Users')

def hash_password(password):
    # simple SHA256, can improve with salt
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_admin_user(email, password):
    item = {
        'email': email,
        'password': hash_password(password),
        'is_superuser': True,
        'created_at': datetime.utcnow().isoformat()
    }
    users_table.put_item(Item=item)
    print(f"Admin user {email} created.")

if __name__ == "__main__":
    create_admin_user("admin@warehouse.com", "Admin123!")  # change password
