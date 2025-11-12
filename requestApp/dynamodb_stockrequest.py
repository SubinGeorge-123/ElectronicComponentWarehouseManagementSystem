import boto3
import uuid
from datetime import datetime
from django.conf import settings
from boto3.dynamodb.conditions import Attr

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
stock_request_table = dynamodb.Table('StockRequests')

class StockRequestDB:
    @staticmethod
    def create(customer_email, stock_id, quantity, status='PENDING', admin_note=''):
        request_id = str(uuid.uuid4())
        item = {
            'request_id': request_id,
            'customer_email': customer_email,
            'stock_id': str(stock_id),
            'quantity': int(quantity),
            'status': status,
            'admin_note': admin_note,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        stock_request_table.put_item(Item=item)
        return item

    @staticmethod
    def get(request_id):
        resp = stock_request_table.get_item(Key={'request_id': request_id})
        return resp.get('Item')

    @staticmethod
    def update(request_id, data):
        data['updated_at'] = datetime.utcnow().isoformat()
        update_expr = "SET " + ", ".join(f"{k}= :{k}" for k in data.keys())
        expr_values = {f":{k}": v for k, v in data.items()}
        stock_request_table.update_item(
            Key={'request_id': request_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )

    @staticmethod
    def delete(request_id):
        stock_request_table.delete_item(Key={'request_id': request_id})

    @staticmethod
    def get_by_customer(customer_email):
        response = stock_request_table.scan(
            FilterExpression=Attr('customer_email').eq(customer_email)
        )
        return response.get('Items', [])
