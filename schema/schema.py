from sqlalchemy import (
    BIGINT, Column, ForeignKey,
    Index, Integer, String, TIMESTAMP
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class Customer(Base):
    """ Table to hold the individual customer data"""
    __tablename__ = 'customer'

    uuid = Column(UUID, primary_key=True)
    email = Column(String)
    fname = Column(String)
    lname = Column(String)

    accounts = relationship('CreditAccount', backref='customer',
                            cascade='all, delete, delete-orphan',
                            single_parent=True)

    def __repr__(self):
        return "<Customer()>" % ()


class CreditAccount(Base):
    """ Table to hold the credit line information """
    __tablename__ = 'credit_account'

    uuid = Column(UUID, primary_key=True)
    customer_uuid = Column(UUID, ForeignKey('customer.uuid'), nullable=False)
    time_opened = Column(TIMESTAMP)
    apr = Column(Integer)
    max_credit = Column(BIGINT)

    payments = relationship('Payment', backref='credit_account',
                            cascade='all, delete, delete-orphan',
                            single_parent=True)
    withdrawals = relationship('Withdrawal', backref='credit_account',
                               cascade='all, delete, delete-orphan',
                               single_parent=True)
    balances = relationship('Balance', backref='credit_account',
                            cascade='all, delete, delete-orphan',
                            single_parent=True)

    def __repr__(self):
        return "<CreditAccount()>" % ()


class Payment(Base):
    __tablename__ = 'payment'
    uuid = Column(UUID, primary_key=True)
    credit_account_uuid = Column(UUID, ForeignKey('credit_account.uuid'),
                                 nullable=False)
    amount = Column(BIGINT)
    time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Payments()>" % ()


class Withdrawal(Base):
    __tablename__ = 'withdrawal'
    uuid = Column(UUID, primary_key=True)
    credit_account_uuid = Column(UUID, ForeignKey('credit_account.uuid'),
                                 nullable=False)
    amount = Column(BIGINT)
    time = Column(TIMESTAMP)

    def __repr__(self):
        return "<Withdrawals()>" % ()


class Balance(Base):
    __tablename__ = 'balance'
    uuid = Column(UUID, primary_key=True)
    credit_account_uuid = Column(UUID, ForeignKey('credit_account.uuid'),
                                 nullable=False)
    time = Column(TIMESTAMP)
    available_credit = Column(BIGINT)
    principal_owed = Column(BIGINT)
    interest_owed = Column(BIGINT)

    idx_balance_time = Index('idx_balance_time', time)

    def __repr__(self):
        return "<Balance()>" % ()
