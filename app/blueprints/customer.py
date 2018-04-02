from flask import Blueprint
from flask_apispec import doc, marshal_with, use_kwargs

from app.controllers.customer import CustomerController
from app.schema.response import CustomerGetResponse
from app.schema.request import AddCustomerRequest

customer_blueprint = Blueprint("customer", __name__)


@customer_blueprint.route('/<string:uuid>', methods=['GET'])
@marshal_with(CustomerGetResponse)
@doc()
def get_customer(uuid):
    customer = CustomerController.get(uuid)
    return(dict(customer=customer))


@customer_blueprint.route('/', methods=['POST'])
@use_kwargs(AddCustomerRequest)
@marshal_with(CustomerGetResponse)
@doc()
def add_customer(email, fname, lname):
    customer = CustomerController.add(email, fname, lname)
    return(dict(customer=customer))
