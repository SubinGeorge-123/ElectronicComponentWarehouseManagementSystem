from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
import json
import boto3
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import StockRequest
from stockApp.models import Stock
from .dynamodb_stockrequest import StockRequestDB
from customerApp.dynamodb import CustomerDB  # since customer now in DynamoDB


def invoke_lambda_recommendation(stock_id, requested_qty):
    """
    Calls AWS Lambda that returns recommendation {"recommendation":"APPROVE"/"REJECT", "message": "..."}
    Fallback uses direct logic.
    """
    try:
        client = boto3.client('lambda', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
        payload = {
            'stock_id': stock_id,
            'requested_quantity': requested_qty
        }
        resp = client.invoke(
            FunctionName=getattr(settings, 'APPROVAL_LAMBDA_NAME', 'stockApprovalLambda'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload),
        )
        data = json.loads(resp['Payload'].read())
        # Lambda might return nested body
        if isinstance(data, dict) and 'body' in data:
            body = data['body']
            if isinstance(body, str):
                body = json.loads(body)
            return body
        return data
    except Exception as e:
        print("Lambda invoke error:", e)
        # Fallback logic
        stock = Stock.objects.filter(id=stock_id).first()
        if stock and stock.quantity >= requested_qty:
            return {'recommendation': 'APPROVE', 'message': 'Stock available (fallback).'}
        return {'recommendation': 'REJECT', 'message': 'Insufficient stock (fallback).'}

def proceed_request(request, req_id):
    if not request.user.is_superuser:
        return redirect('login')

    req = StockRequestDB.get(req_id)
    if not req:
        messages.error(request, "Request not found.")
        return redirect('admin_dashboard')

    # fetch stock info from SQL
    stock = Stock.objects.filter(id=req['stock_id']).first()
    if not stock:
        messages.error(request, "Stock not found.")
        return redirect('admin_dashboard')

    rec = invoke_lambda_recommendation(stock.id, req['quantity'])

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '')

        if action == 'approve':
            if stock.quantity >= req['quantity']:
                stock.quantity -= req['quantity']
                stock.save()
                StockRequestDB.update(req_id, {'status': 'APPROVED', 'admin_note': admin_note})
                # notify via SES
                try:
                    ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                    ses.send_email(
                        Source=settings.DEFAULT_FROM_EMAIL,
                        Destination={'ToAddresses': [req['customer_email']]},
                        Message={
                            'Subject': {'Data': 'Stock Request Approved'},
                            'Body': {'Text': {'Data': f"Your request for {stock.name} has been approved."}}
                        }
                    )
                except Exception as e:
                    print("SES error:", e)
                messages.success(request, "Request approved.")
            else:
                messages.error(request, "Not enough stock.")
        else:
            StockRequestDB.update(req_id, {'status': 'REJECTED', 'admin_note': admin_note})
            try:
                ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                ses.send_email(
                    Source=settings.DEFAULT_FROM_EMAIL,
                    Destination={'ToAddresses': [req['customer_email']]},
                    Message={
                        'Subject': {'Data': 'Stock Request Rejected'},
                        'Body': {'Text': {'Data': f"Your request was rejected. Note: {admin_note}"}}
                    }
                )
            except Exception as e:
                print("SES error:", e)
            messages.success(request, "Request rejected.")
        return redirect('admin_dashboard')

    return rende

