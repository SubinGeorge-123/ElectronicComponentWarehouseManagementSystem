from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
import json
import boto3
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import StockRequest
from stockApp.models import Stock

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
    req = get_object_or_404(StockRequest, id=req_id)
    # call lambda to get recommendation
    rec = invoke_lambda_recommendation(req.stock.id, req.quantity)
    # We show recommendation but allow admin to force action.
    if request.method == 'POST':
        action = request.POST.get('action')  # 'approve' or 'reject'
        admin_note = request.POST.get('admin_note', '')
        if action == 'approve':
            if req.stock.quantity >= req.quantity:
                req.stock.quantity -= req.quantity
                req.stock.save()
                req.status = 'APPROVED'
                req.admin_note = admin_note
                req.save()
                # send SES to customer
                try:
                    ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                    ses.send_email(
                        Source=settings.DEFAULT_FROM_EMAIL,
                        Destination={'ToAddresses': [req.customer.email]},
                        Message={
                            'Subject': {'Data': 'Your stock request has been approved'},
                            'Body': {'Text': {'Data': f"Your request #{req.id} for {req.stock.name} has been approved."}}
                        }
                    )
                except Exception as e:
                    print("SES error:", e)
                messages.success(request, "Request approved.")
            else:
                messages.error(request, "Not enough stock to approve.")
        else:
            req.status = 'REJECTED'
            req.admin_note = admin_note
            req.save()
            # send rejection email
            try:
                ses = boto3.client('ses', region_name=getattr(settings, 'AWS_REGION', 'us-east-1'))
                ses.send_email(
                    Source=settings.DEFAULT_FROM_EMAIL,
                    Destination={'ToAddresses': [req.customer.email]},
                    Message={
                        'Subject': {'Data': 'Your stock request has been rejected'},
                        'Body': {'Text': {'Data': f"Your request #{req.id} has been rejected. Note: {admin_note}"}}
                    }
                )
            except Exception as e:
                print("SES error:", e)
            messages.success(request, "Request rejected.")
        return redirect('admin_dashboard')

    # GET -> show confirmation page with recommendation
    return render(request, 'proceed_request.html', {'req': req, 'recommendation': rec})
