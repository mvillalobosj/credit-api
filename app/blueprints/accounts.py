from datetime import datetime

from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

from app.controllers.accounts import AccountController
from app.schema.response import AccountGetResponse
from app.schema.request import (
    AddAccountRequest, AddPaymentRequest, AddWithdrawalRequest,
    GetAccountRequest)

accounts_blueprint = Blueprint("accounts", __name__)


@accounts_blueprint.route('/<string:uuid>', methods=['GET'])
@use_kwargs(GetAccountRequest)
@marshal_with(AccountGetResponse)
@doc()
def get_account(uuid, time=datetime.now()):
    account = AccountController.get_account(uuid, time)
    return(dict(account=account))


@accounts_blueprint.route('/', methods=['POST'])
@use_kwargs(AddAccountRequest)
@marshal_with(AccountGetResponse)
@doc()
def add_account(customer_uuid, apr, max_credit, time_opened):
    account = AccountController.open_account(
        customer_uuid, apr, max_credit, time_opened)
    return(dict(account=account))


@accounts_blueprint.route('/payment', methods=['POST'])
@use_kwargs(AddPaymentRequest)
@marshal_with(AccountGetResponse)
@doc()
def make_payment(account_uuid, amount, time):
    account = AccountController.payment(account_uuid, amount, time)
    return(dict(account=account))


@accounts_blueprint.route('/withdrawal', methods=['POST'])
@use_kwargs(AddWithdrawalRequest)
@marshal_with(AccountGetResponse)
@doc()
def make_withdrawal(account_uuid, amount, time):
    account = AccountController.withdrawal(account_uuid, amount, time)
    return(dict(account=account))
