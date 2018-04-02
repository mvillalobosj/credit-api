import uuid

from flask import current_app

from app.utilities import APIError, SC
from schema import Customer


def serialize_customer(customer):
    return dict(
        uuid=customer.uuid,
        email=customer.email,
        fname=customer.fname,
        lname=customer.lname)


class CustomerController:

    @staticmethod
    def add(email, fname, lname):
        customer = Customer(
            uuid=str(uuid.uuid4()),
            email=email,
            fname=fname,
            lname=lname)
        current_app.db.add(customer)
        current_app.db.commit()
        return serialize_customer(customer)

    @staticmethod
    def get(uuid):
        customer = current_app.db.query(Customer).get(uuid)
        if not customer:
            raise APIError("Customer not found", SC.NOT_FOUND)
        return serialize_customer(customer)
