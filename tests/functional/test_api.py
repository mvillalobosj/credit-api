import pytest
import uuid

from datetime import datetime
import requests

base_url = "http://api:5001"


def post_request(url, payload):
    request_url = base_url + url
    response = requests.post(request_url, data=payload)

    response.raise_for_status()
    return response.json()


def get_request(url, params=None):
    request_url = base_url + url
    response = requests.get(request_url, params=params)
    response.raise_for_status()
    return response.json()


def get_customer(uuid):
    return get_request("/customer/" + uuid)


def get_account(uuid, time=None):
    params = None
    if time:
        params = {'time': time}
    return get_request("/accounts/" + uuid, params)


def new_customer(
        fname="Michael", lname="Villalobos", email="mvillalobosj@yahoo.com"):
    customer_payload = {
        "fname": fname,
        "lname": lname,
        "email": email
    }

    return post_request("/customer/", customer_payload)


def new_account(apr, max_credit, time_opened=datetime.now()):
    customer = new_customer()
    account_payload = {
        "customerUUID": customer['customer']['uuid'],
        "apr": apr,
        "maxCredit": max_credit,
        "timeOpened": time_opened
    }
    return post_request("/accounts/", account_payload)


def make_payment(account_uuid, amount, time=datetime.now()):
    payment_payload = {
        "accountUUID": account_uuid,
        "amount": amount,
        "time": time
    }
    return post_request("/accounts/payment", payment_payload)


def make_withdrawal(account_uuid, amount, time=datetime.now()):
    withdrawal_payload = {
        "accountUUID": account_uuid,
        "amount": amount,
        "time": time
    }
    return post_request("/accounts/withdrawal", withdrawal_payload)


class TestCustomer:

    def test_make_customer(self):
        fname = "John"
        lname = "Doe"
        email = "john.doe@fair.com"

        customer = new_customer(fname, lname, email)

        assert customer['customer']['email'] == email
        assert customer['customer']['fname'] == fname
        assert customer['customer']['lname'] == lname

    def test_make_and_get_customer(self):
        fname = "John"
        lname = "Doe"
        email = "john.doe@fair.com"

        customer = new_customer(fname, lname, email)

        customer_uuid = customer['customer']['uuid']

        customer_response = get_customer(customer_uuid)

        assert customer_response['customer']['uuid'] == customer_uuid
        assert customer_response['customer']['email'] == email
        assert customer_response['customer']['fname'] == fname
        assert customer_response['customer']['lname'] == lname


class TestAccount:

    def test_create_account(self):
        time_opened = datetime.now()

        account = new_account(
            apr=35,
            max_credit=50000000000,
            time_opened=time_opened)

        time_response = time_opened.isoformat() + "+00:00"
        assert account['account']['apr'] == 35
        assert account['account']['availableCredit'] == 50000000000
        assert account['account']['interestOwed'] == 0
        assert account['account']['maxCredit'] == 50000000000
        assert account['account']['timeOpened'] == time_response

    def test_get_account(self):
        time_opened = datetime.now()

        account = new_account(
            apr=35,
            max_credit=50000000000,
            time_opened=time_opened)

        account_uuid = account['account']['uuid']

        account_response = get_account(account_uuid)
        time_response = time_opened.isoformat() + "+00:00"

        assert account_response['account']['apr'] == 35
        assert account_response['account']['availableCredit'] == 50000000000
        assert account_response['account']['interestOwed'] == 0
        assert account_response['account']['principalOwed'] == 0
        assert account_response['account']['maxCredit'] == 50000000000
        assert account_response['account']['timeOpened'] == time_response

    def test_make_withdrawal(self):
        account = new_account(
            apr=35,
            max_credit=50000000000)

        account_uuid = account['account']['uuid']

        response = make_withdrawal(account_uuid, 10000000000)

        assert response['account']['availableCredit'] == 40000000000
        assert response['account']['interestOwed'] == 0
        assert response['account']['principalOwed'] == 10000000000
        assert response['account']['maxCredit'] == 50000000000

    def test_make_withdrawal_then_payment(self):
        account = new_account(
            apr=35,
            max_credit=50000000000)

        account_uuid = account['account']['uuid']

        make_withdrawal(account_uuid, 30000000000)

        response = make_payment(account_uuid, 10000000000)

        assert response['account']['availableCredit'] == 30000000000
        assert response['account']['interestOwed'] == 0
        assert response['account']['principalOwed'] == 20000000000
        assert response['account']['maxCredit'] == 50000000000


class TestInterest:

    def test_one_withdrawal_one_pay_period(self):
        open_time = datetime(year=2017, month=10, day=1)
        withdrawal_time = datetime(year=2017, month=10, day=1)
        check_time = datetime(year=2017, month=10, day=31)

        account = new_account(
            apr=35,
            max_credit=100000000000,
            time_opened=open_time)

        account_uuid = account['account']['uuid']

        make_withdrawal(account_uuid, 50000000000, time=withdrawal_time)

        response = get_account(account_uuid, check_time)

        assert response['account']['availableCredit'] == 48561643836
        assert response['account']['interestOwed'] == 1438356164
        assert response['account']['principalOwed'] == 50000000000
        assert response['account']['maxCredit'] == 100000000000

    def test_multiple_withdrawal_and_payment_one_pay_period(self):
        open_time = datetime(year=2017, month=10, day=1)
        withdrawal_time = datetime(year=2017, month=10, day=1)
        payment_time = datetime(year=2017, month=10, day=16)
        withdrawal_time_2 = datetime(year=2017, month=10, day=26)
        check_time = datetime(year=2017, month=10, day=31)

        account = new_account(
            apr=35,
            max_credit=100000000000,
            time_opened=open_time)

        account_uuid = account['account']['uuid']

        make_withdrawal(account_uuid, 50000000000, time=withdrawal_time)
        make_payment(account_uuid, 20000000000, time=payment_time)
        make_withdrawal(account_uuid, 10000000000, time=withdrawal_time_2)

        response = get_account(account_uuid, check_time)

        assert response['account']['interestOwed'] == 1198630137
        assert response['account']['availableCredit'] == 58801369863
        assert response['account']['principalOwed'] == 40000000000
        assert response['account']['maxCredit'] == 100000000000

    def test_multiple_pay_periods(self):
        open_time = datetime(year=2017, month=10, day=1)
        withdrawal_time = datetime(year=2017, month=10, day=1)
        payment_time = datetime(year=2017, month=10, day=16)
        withdrawal_time_2 = datetime(year=2017, month=10, day=26)
        check_time = datetime(year=2017, month=12, day=1)

        account = new_account(
            apr=35,
            max_credit=100000000000,
            time_opened=open_time)

        account_uuid = account['account']['uuid']

        make_withdrawal(account_uuid, 50000000000, time=withdrawal_time)
        make_payment(account_uuid, 20000000000, time=payment_time)
        make_withdrawal(account_uuid, 10000000000, time=withdrawal_time_2)

        response = get_account(account_uuid, check_time)

        assert response['account']['interestOwed'] == 2349315069
        assert response['account']['availableCredit'] == 57650684931
        assert response['account']['principalOwed'] == 40000000000
        assert response['account']['maxCredit'] == 100000000000

    def test_recent_pay_periods_previous_payments(self):
        open_time = datetime(year=2017, month=10, day=1)
        withdrawal_time = datetime(year=2017, month=10, day=5)
        payment_time = datetime(year=2017, month=10, day=16)
        withdrawal_time_2 = datetime(year=2017, month=11, day=5)
        check_time = datetime(year=2017, month=12, day=1)

        account = new_account(
            apr=35,
            max_credit=100000000000,
            time_opened=open_time)

        account_uuid = account['account']['uuid']

        make_withdrawal(account_uuid, 50000000000, time=withdrawal_time)
        make_payment(account_uuid, 20000000000, time=payment_time)
        make_withdrawal(account_uuid, 10000000000, time=withdrawal_time_2)

        response = get_account(account_uuid, check_time)
        print(response)
        assert response['account']['interestOwed'] == 1102739726
        assert response['account']['availableCredit'] == 58897260274
        assert response['account']['principalOwed'] == 40000000000
        assert response['account']['maxCredit'] == 100000000000


class TestNegative:

    def test_non_existing_customer(self):
        with pytest.raises(requests.HTTPError):
            response = get_customer(str(uuid.uuid4()))
            assert response.status_code == 404

    def test_non_existing_account(self):
        with pytest.raises(requests.HTTPError):
            response = get_account(str(uuid.uuid4()))
            assert response.status_code == 404

    def test_make_invalid_payment(self):
        account = new_account(
            apr=35,
            max_credit=50000000000)

        account_uuid = account['account']['uuid']

        with pytest.raises(requests.HTTPError):
            response = make_payment(account_uuid, 10000000000)
            assert response.status_code == 422

        with pytest.raises(requests.HTTPError):
            response = make_payment(account_uuid, 0)
            assert response.status_code == 422

        with pytest.raises(requests.HTTPError):
            response = make_payment(account_uuid, -10000000000)
            assert response.status_code == 422

    def test_make_invalid_withdrawal(self):
        account = new_account(
            apr=35,
            max_credit=50000000000)

        account_uuid = account['account']['uuid']

        with pytest.raises(requests.HTTPError):
            response = make_withdrawal(account_uuid, 60000000000)
            assert response.status_code == 422

        with pytest.raises(requests.HTTPError):
            response = make_withdrawal(account_uuid, 0)
            assert response.status_code == 422

        with pytest.raises(requests.HTTPError):
            response = make_withdrawal(account_uuid, -60000000000)
            assert response.status_code == 422
