from marshmallow import fields, Schema


class CustomerResponse(Schema):
    uuid = fields.String()
    fname = fields.String()
    lname = fields.String()
    email = fields.String()


class CustomerGetResponse(Schema):
    customer = fields.Nested(CustomerResponse)


class AccountResponse(Schema):
    uuid = fields.String()
    apr = fields.Integer()
    max_credit = fields.Integer(dump_to='maxCredit')
    time_opened = fields.DateTime(dump_to='timeOpened')
    available_credit = fields.Integer(dump_to='availableCredit')
    principal_owed = fields.Integer(dump_to='principalOwed')
    interest_owed = fields.Integer(dump_to='interestOwed')


class AccountGetResponse(Schema):
    account = fields.Nested(AccountResponse)
