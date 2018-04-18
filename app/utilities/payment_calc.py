from datetime import timedelta


def make_payment(principal_owed, interest_owed, payment):
    """ Takes in the current principal and interest balances and a payment
    and returns a tuple consisting of the new principal and interest. Payments
    will first reduce the interest balance before reducing the principal
    balance.

    Args:
        principal_owed (int) - The current principal balance
        interest_owed (int) - The current interest balance
        payment (int) - The payment amount

    Returns:
        (int, int) - A tuple containing the following (principal, interest)
    """
    if payment < 0:
        raise ValueError("Cannot make negative payment")
    if payment == 0:
        raise ValueError("Payment must be greater than 0")
    if payment > (principal_owed + interest_owed):
        raise ValueError(
            "Payment must be less than or equal to current balance.")

    if payment >= interest_owed:
        # reduce interest balance before reducing principal balance
        payment -= interest_owed
        interest_owed = 0
        principal_owed -= payment
    else:
        # can only reduce interest balance
        interest_owed -= payment

    return (principal_owed, interest_owed)


def make_withdrawal(available_credit, amount):
    """ Takes in the current available credit and the amount to withdraw and
    returns the new available credit after the withdrawal.

    Args:
        available_credit (int) - The current available credit
        amount (int) - The amount to withdraw

    Returns:
        int - The new available credit
    """
    if amount < 0:
        raise ValueError("Cannot withdraw negative amount")
    if amount == 0:
        raise ValueError("Withdrawal amount must be greater than 0")
    if amount > available_credit:
        raise ValueError(
            "Withdrawal amount cannot exceed available credit.")

    return available_credit - amount


def _get_interest(principal_owed, number_of_days, apr):
    return round(principal_owed * number_of_days * apr / 36500)


def _calc_interest_over_balances(apr, balance_history):
    """ Calculates interest over an arbitrary balance history list.

    Args:
        apr (int) - The APR for the credit line.
        balance_history (list) - A list of dictionaries containing the
                                following keys:
            {
                'time': (datetime) - the time the balance was recorded
                'principal_owed': (int) - the amount of principal owed
            }

    Returns:
        Total interest over balance history.
    """
    # First inject a starting balance at the beginning of the period.

    interest = 0
    for i in range(len(balance_history) - 1):
        principal_owed = balance_history[i]['principal_owed']
        number_of_days = (
            balance_history[i + 1]['time'] - balance_history[i]['time']).days
        interest += _get_interest(principal_owed, number_of_days, apr)
    return interest


def get_monthly_interests(apr, pay_period, end_date, balance_history):
    """ Calculates the interests owed per month since the last balance was
    calculated

    Args:
        apr (int) - The APR for the credit line.
        pay_period (int) - The number of days per pay period
        credit_start_date (datetime) - THe time the credit line was started
        end_date (datetime) - The time to stop calculating interest
        balance_history (list(dict)) - A list of dictionaries containing the
                                       following keys:
            {
                'time': (datetime) - the time the balance was recorded
                'principal_owed': (int) - the amount of principal owed
            }
            This list assumes the first entry is the opening balance of the
            account and that the list is sorted by time ascending.

    Returns:
        list[(int, time)] - A list of tuples containing time and interest
                            amounts since the last balance was calculated.
    """
    interests = []

    first_balance = balance_history[0]
    last_balance = balance_history[-1]
    first_date = first_balance['time']

    # get the last eligible day to calculate interest.
    days_since_account_opened = (end_date - first_date).days
    days_since_last_pay_period = days_since_account_opened % pay_period

    interest_calc_date = end_date - timedelta(days=days_since_last_pay_period)

    # keep track of the last principal owed
    principal_owed = last_balance['principal_owed']

    balance_index = len(balance_history) - 1
    found_balances = False
    while interest_calc_date > first_date:
        previous_pay_date = interest_calc_date - timedelta(days=pay_period)

        # Create an end date for the balance calculator, principal doesn't
        # matter as it won't be factored in the interest calculation
        balances = [{
            'time': interest_calc_date,
            'principal_owed': 0
        }]

        # Loop through all recorded balances that are within this pay period
        # and append them to the balances list
        while (balance_history[balance_index]['time'] >= previous_pay_date and
               balance_index >= 0):

            if balance_history[balance_index]['time'] <= interest_calc_date:
                balances.append(balance_history[balance_index])

            balance_index -= 1
            found_balances = True

        # Append a new balance for the calculation at the start of the pay
        # period. Set the principal owed to the previous balance's principal
        # owed or zero if we've exhausted the list.
        if balance_index >= 0:
            principal_owed = balance_history[balance_index]['principal_owed']
        else:
            principal_owed = 0

        balances.append({
            'time': previous_pay_date,
            'principal_owed': principal_owed
        })

        # Since going backwards over the history, balances will be in reverse
        # order, so need to reverse again for the interest calculation
        interest_amount = _calc_interest_over_balances(apr, balances[::-1])

        # If we have calculated interest for later pay periods, we need
        # to make sure we add it to the new interest balances.
        for interest in interests:
            interest[0] += interest_amount

        interests.append([interest_amount, interest_calc_date])

        if found_balances:
            # If we've found balances that means interest was already
            # calculated for those periods and we should stop calculating.
            break

        # Set the new interest calc date.
        interest_calc_date = previous_pay_date

    return interests[::-1]
