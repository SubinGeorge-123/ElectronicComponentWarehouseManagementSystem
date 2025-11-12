import uuid
import boto3
from datetime import datetime
from django.conf import settings

dynamodb = boto3.resource('dynamodb', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
stock_table = dynamodb.Table('Stocks')

s3 = boto3.client('s3', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
S3_BUCKET = getattr(settings, 'AWS_S3_BUCKET_NAME', 'your-s3-bucket-name')

class StockDB:
    @staticmethod
    def create(name, category, quantity, price, image_file=None):
        stock_id = str(uuid.uuid4())
        image_url = None

        if image_file:
            s3_key = f"stock_images/{stock_id}_{image_file.name}"
            s3.upload_fileobj(image_file, S3_BUCKET, s3_key, ExtraArgs={'ContentType': image_file.content_type})
            image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

        item = {
            'stock_id': stock_id,
            'name': name,
            'category': category,
            'quantity': int(quantity),
            'price': float(price),
            'image_url': image_url or '',
            'created_at': datetime.utcnow().isoformat()
        }
        stock_table.put_item(Item=item)
        return item

    @staticmethod
    def get(stock_id):
        resp = stock_table.get_item(Key={'stock_id': stock_id})
        return resp.get('Item')

    @staticmethod
    def update(stock_id, data, new_image=None):
        if new_image:
            s3_key = f"stock_images/{stock_id}_{new_image.name}"
            s3.upload_fileobj(new_image, S3_BUCKET, s3_key, ExtraArgs={'ContentType': new_image.content_type})
            data['image_url'] = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

        data['updated_at'] = datetime.utcnow().isoformat()
        update_expr = "SET " + ", ".join(f"{k}= :{k}" for k in data.keys())
        expr_values = {f":{k}": v for k, v in data.items()}
        stock_table.update_item(
            Key={'stock_id': stock_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )

    @staticmethod
    def delete(stock_id):
        stock_table.delete_item(Key={'stock_id': stock_id})

    @staticmethod
    def all():
        """Return all stocks (scan entire table)"""
        resp = stock_table.scan()
        return resp.get('Items', [])
