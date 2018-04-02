from datetime import datetime
from marshmallow import fields, Schema


class GetAccountRequest(Schema):
    time = fields.DateTime(missing=datetime.now())


class AddCustomerRequest(Schema):
    email = fields.String(required=True)
    fname = fields.String(required=True)
    lname = fields.String(required=True)


class AddAccountRequest(Schema):
    customer_uuid = fields.String(required=True, load_from='customerUUID')
    time_opened = fields.DateTime(default=datetime.now(),
                                  load_from='timeOpened')
    apr = fields.Integer(required=True)
    max_credit = fields.Integer(load_from='maxCredit', required=True)


class AddPaymentRequest(Schema):
    account_uuid = fields.String(required=True, load_from='accountUUID')
    time = fields.DateTime(default=datetime.now())
    amount = fields.Integer(required=True)


class AddWithdrawalRequest(Schema):
    account_uuid = fields.String(required=True, load_from='accountUUID')
    time = fields.DateTime(default=datetime.now())
    amount = fields.Integer(required=True)
