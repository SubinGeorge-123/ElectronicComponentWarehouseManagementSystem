import boto3
from datetime import datetime
from django.conf import settings

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
customer_table = dynamodb.Table('Customers')  # make sure this matches your DynamoDB table name

class CustomerDB:
    @staticmethod
    def create(user_id, first_name, last_name, email):
        """Create a new customer record in DynamoDB"""
        item = {
            'email': email,  # Partition key
            'user_id': str(user_id),
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow().isoformat()
        }
        customer_table.put_item(Item=item)
        return item

    @staticmethod
    def get(email):
        """Fetch customer by email"""
        response = customer_table.get_item(Key={'email': email})
        return response.get('Item')

    @staticmethod
    def update(email, data):
        """Update customer attributes"""
        update_expr = "SET " + ", ".join(f"{k}= :{k}" for k in data.keys())
        expr_values = {f":{k}": v for k, v in data.items()}
        customer_table.update_item(
            Key={'email': email},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )

    @staticmethod
    def delete(email):
        """Delete customer"""
        customer_table.delete_item(Key={'email': email})
