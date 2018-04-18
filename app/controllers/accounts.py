import uuid

from flask import current_app

from app.utilities import (
    APIError, get_monthly_interests, make_payment, make_withdrawal, SC)
from schema import Balance, CreditAccount, Customer, Payment, Withdrawal


def serialize_account(account):
    last_balance = account.balances[-1]

    return dict(
        uuid=account.uuid,
        apr=account.apr,
        max_credit=account.max_credit,
        time_opened=account.time_opened,
        available_credit=last_balance.available_credit,
        principal_owed=last_balance.principal_owed,
        interest_owed=last_balance.interest_owed
    )


def _get_account(account_uuid):
    account = current_app.db.query(CreditAccount).get(account_uuid)

    if not account:
        raise APIError("Account not found", SC.NOT_FOUND)
    return account


def _create_balance(time, principal_owed, interest_owed, max_credit):
    return Balance(
        uuid=str(uuid.uuid4()),
        time=time,
        principal_owed=principal_owed,
        interest_owed=interest_owed,
        available_credit=max_credit - (principal_owed + interest_owed))


class AccountController:
    @staticmethod
    def open_account(customer_uuid, apr, max_credit, opening_time):
        customer = current_app.db.query(Customer).get(customer_uuid)

        if not customer:
            raise APIError("Customer not found", SC.NOT_FOUND)

        account = CreditAccount(
            uuid=str(uuid.uuid4()),
            time_opened=opening_time,
            apr=apr,
            max_credit=max_credit)

        opening_balance = _create_balance(
            time=opening_time,
            principal_owed=0,
            interest_owed=0,
            max_credit=max_credit)

        account.balances.append(opening_balance)
        customer.accounts.append(account)

        current_app.db.add(opening_balance)
        current_app.db.add(account)
        current_app.db.add(customer)
        current_app.db.commit()
        return serialize_account(account)

    @staticmethod
    def get_account(account_uuid, time):
        account = _get_account(account_uuid)
        AccountController.update_balances(account_uuid, time)

        return serialize_account(account)

    @staticmethod
    def update_balances(account_uuid, as_of_date):
        account = _get_account(account_uuid)

        balances = [
            dict(time=row.time, principal_owed=row.principal_owed)
            for row in account.balances
        ]

        interests = get_monthly_interests(
            account.apr, 30, as_of_date, balances
        )

        last_balance = account.balances[-1]
        principal_owed = last_balance.principal_owed

        for (interest_owed, calc_date) in interests:
            last_balance = _create_balance(
                time=calc_date,
                principal_owed=principal_owed,
                interest_owed=interest_owed,
                max_credit=account.max_credit
            )

            account.balances.append(last_balance)

        current_app.db.add(account)
        current_app.db.commit()

        return last_balance

    @staticmethod
    def payment(account_uuid, payment, time):
        account = _get_account(account_uuid)

        last_balance = AccountController.update_balances(account_uuid, time)
        principal_owed = last_balance.principal_owed
        interest_owed = last_balance.interest_owed

        try:
            principal, interest = make_payment(
                principal_owed, interest_owed, payment)
        except ValueError as ex:
            raise APIError(str(ex), SC.UNPROCESSABLE)

        account.balances.append(
            _create_balance(
                time=time,
                principal_owed=principal,
                interest_owed=interest,
                max_credit=account.max_credit
            )
        )

        account.payments.append(
            Payment(
                uuid=str(uuid.uuid4()),
                amount=payment,
                time=time
            )
        )

        current_app.db.add(account)
        current_app.db.commit()
        return serialize_account(account)

    @staticmethod
    def withdrawal(account_uuid, withdrawal_amount, time):
        account = _get_account(account_uuid)
        last_balance = AccountController.update_balances(account_uuid, time)
        available_credit = last_balance.available_credit

        try:
            make_withdrawal(available_credit, withdrawal_amount)
        except ValueError as ex:
            raise APIError(str(ex), SC.UNPROCESSABLE)

        principal_owed = last_balance.principal_owed + withdrawal_amount
        interest_owed = last_balance.interest_owed

        account.balances.append(
            _create_balance(
                time=time,
                principal_owed=principal_owed,
                interest_owed=interest_owed,
                max_credit=account.max_credit
            )
        )

        account.withdrawals.append(
            Withdrawal(
                uuid=str(uuid.uuid4()),
                amount=withdrawal_amount,
                time=time
            )
        )
        current_app.db.add(account)
        current_app.db.commit()
        return serialize_account(account)
