from datetime import datetime
import app.lib.payment_calc as calc

import pytest


class TestMakePayment():
    @pytest.mark.parametrize(
        "principal_owed,interest_owed,payment,new_principal,new_interest",
        [
            (200, 0, 100, 100, 0),    # test with no interest
            (200, 100, 100, 200, 0),  # test with payment matching interest
            (200, 100, 300, 0, 0),    # test full payment
            (200, 100, 99, 200, 1)    # test interest not fully paid
        ])
    def test_allowed_payments(
            self, principal_owed, interest_owed, payment,
            new_principal, new_interest):

        test_principal, test_interest = calc.make_payment(
            principal_owed, interest_owed, payment)

        assert test_principal == new_principal
        assert test_interest == new_interest

    def test_payment_greater_than_total_balance(self):
        principal_owed = 200
        interest_owed = 100
        payment = 301

        with pytest.raises(ValueError):
            calc.make_payment(principal_owed, interest_owed, payment)

    def test_negative_payment(self):
        principal_owed = 200
        interest_owed = 100
        payment = -1

        with pytest.raises(ValueError):
            calc.make_payment(principal_owed, interest_owed, payment)

    def test_zero_payment(self):
        principal_owed = 200
        interest_owed = 100
        payment = 0

        with pytest.raises(ValueError):
            calc.make_payment(principal_owed, interest_owed, payment)


class TestMakeWithdrawal():
    @pytest.mark.parametrize(
        "available_credit,amount,new_amount",
        [
            (200, 200, 0),    # test full withdrawal
            (200, 100, 100),  # test partial withdrawal
        ])
    def test_allowed_withdrawals(
            self, available_credit, amount, new_amount):

        test_amount = calc.make_withdrawal(available_credit, amount)
        assert test_amount == new_amount

    def test_withdrawal_greater_than_available(self):
        amount = 100
        available_credit = 50

        with pytest.raises(ValueError):
            calc.make_withdrawal(available_credit, amount)

    def test_negative_withdrawal(self):
        amount = -1
        available_credit = 50

        with pytest.raises(ValueError):
            calc.make_withdrawal(available_credit, amount)

    def test_zero_withdrawal(self):
        amount = 0
        available_credit = 50

        with pytest.raises(ValueError):
            calc.make_withdrawal(available_credit, amount)


class TestGetInterest():
    @pytest.mark.parametrize(
        "principal_owed,number_of_days,apr,value",
        [
            (50000000000, 30, 35, 1438356164),  # Test standard APR calc
            (0, 30, 1, 0),         # Test no principal is no interest
            (500, 0, 1, 0),        # Test 0 number of days is no interest
            (500, 30, 0, 0),       # Test no apr is no interest
        ])
    def test_get_interest(
            self, principal_owed, number_of_days, apr, value):
        test_value = calc._get_interest(principal_owed, number_of_days, apr)
        assert int(test_value) == value


class TestCalcInterestOverBalance():
    @pytest.mark.parametrize(
        "apr,balance_history,interest", [
            (
                35,
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=20),
                    'principal_owed': 30000000000
                }, {
                    'time': datetime(year=2017, month=10, day=31),
                    'principal_owed': 0
                }],
                1227397260
            ),
            (
                35,
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=31),
                    'principal_owed': 0
                }],
                1438356164
            ),
            (
                35,
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }],
                0
            ),
            (
                35,
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=16),
                    'principal_owed': 30000000000
                }, {
                    'time': datetime(year=2017, month=10, day=26),
                    'principal_owed': 40000000000
                }, {
                    'time': datetime(year=2017, month=10, day=31),
                    'principal_owed': 0
                }],
                1198630137
            ),
        ])
    def test_calc_interest(self, apr, balance_history, interest):
        test_interest = calc._calc_interest_over_balances(apr, balance_history)
        assert int(test_interest) == interest


class TestGetMonthlyInterests():
    @pytest.mark.parametrize(
        "apr,pay_period,end_date,balance_history,interests", [
            (
                35,
                30,
                datetime(year=2017, month=10, day=31),
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }, {
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=20),
                    'principal_owed': 30000000000
                }],
                [(1227397260, datetime(year=2017, month=10, day=31))]
            ),
            (
                35,
                30,
                datetime(year=2017, month=10, day=31),
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }, {
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }],
                [(1438356164, datetime(year=2017, month=10, day=31))]
            ),
            (
                35,
                30,
                datetime(year=2017, month=10, day=31),
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }, {
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=16),
                    'principal_owed': 30000000000
                }, {
                    'time': datetime(year=2017, month=10, day=26),
                    'principal_owed': 40000000000
                }],
                [(1198630137, datetime(year=2017, month=10, day=31))]
            ),
            (
                35,
                30,
                datetime(year=2017, month=12, day=1),
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }, {
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=16),
                    'principal_owed': 30000000000
                }, {
                    'time': datetime(year=2017, month=10, day=26),
                    'principal_owed': 40000000000
                }],
                [
                    (1198630137, datetime(year=2017, month=10, day=31)),
                    (2349315069, datetime(year=2017, month=11, day=30))
                ]
            ),
            (
                35,
                30,
                datetime(year=2017, month=12, day=1),
                [{
                    'time': datetime(year=2017, month=10, day=1),
                    'principal_owed': 0
                }, {
                    'time': datetime(year=2017, month=10, day=5),
                    'principal_owed': 50000000000
                }, {
                    'time': datetime(year=2017, month=10, day=16),
                    'principal_owed': 30000000000
                }, {
                    'time': datetime(year=2017, month=11, day=5),
                    'principal_owed': 40000000000
                }],
                [
                    (1102739726, datetime(year=2017, month=11, day=30))
                ]
            )
        ])
    def test_calc_interest(
            self, apr, pay_period, end_date, balance_history, interests):
        test_interests = calc.get_monthly_interests(
            apr, pay_period, end_date, balance_history)
        for i in range(len(interests)):
            assert int(test_interests[i][0]) == interests[i][0]
            assert test_interests[i][1] == interests[i][1]
