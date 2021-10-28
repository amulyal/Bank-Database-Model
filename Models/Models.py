from flask_sqlalchemy import SQLAlchemy
import re
from dateutil import parser
from datetime import datetime

EMAIL_PATTERN = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$"

ACCOUNT_TYPE = {'SAVINGS': 'SA', 'CURRENT': 'CA'}

CARD_TYPE = {'MASTER': 'MASTER',
             'VISA': 'VISA'}

CARD_STATUS = {'NOT_ACTIVE': 'NOT ACTIVATED',
               'ACTIVE': 'ACTIVE',
               'LOST': 'LOST',
               'EXPIRED': 'EXPIRED',
               'CANCELLED': 'CANCELLED'}

CARD_NUMBER_FORMAT = '[0-9]{16}'

PIN_NUMBER_FORMAT = '[0-9]{4}'

CVV_NUMBER_FORMAT = '[0-9]{3}'

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customers"
    __table_args__ = {'schema': 'bank'}
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(500))
    email = db.Column(db.String(100))

    def __init__(self, first_name, last_name, date_of_birth, address, email):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.address = address
        self.email = email

    def validate(self):
        if re.match("^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$",
                    self.email) != None:
            return True
        return False

    def to_json(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "dateOfBirth": self.date_of_birth,
            "address": self.address,
            "email": self.email
        }


class Account(db.Model):
    __tablename__ = "accounts"
    __table_args__ = {'schema': 'bank'}

    account_type = db.Column(db.String(20), primary_key=True)
    account_number = db.Column(db.BigInteger, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('bank.customers.id'))
    open_date = db.Column(db.Date)
    status = db.Column(db.String(20))
    close_date = db.Column(db.DateTime)
    account_balance = db.Column(db.Numeric(precision=15, scale=2))
    last_transaction_date = db.Column(db.DateTime)
    customer = db.relationship("Customer", backref="accounts", lazy=True)

    def __init__(self, account_type, id, open_date, status):
        self.account_type = account_type
        self.id = id
        self.open_date = open_date
        self.status = status

    def to_json(self):
        return {
            "accountType": self.account_type,
            "accountNumber": self.account_number,
            "customer": {
                "id": self.customer.id,
                "firstName": self.customer.first_name,
                "lastName": self.customer.last_name,
                "dateOfBirth": self.customer.date_of_birth,
                "address": self.customer.address,
                "email": self.customer.email
            },
            "accountOpenDate": self.open_date,
            "accountStatus": self.status,
            "accountBalance": self.account_balance,
            "accountCloseDate": self.close_date,
            "LastTransactionDate": self.last_transaction_date
        }


class Card(db.Model):
    __tablename__ = "cards"
    __table_args__ = {'schema': 'bank'}

    card_number = db.Column(db.String(16), primary_key=True)
    account_type = db.Column(db.String(10), db.ForeignKey('bank.accounts.account_type'))
    account_number = db.Column(db.BigInteger, db.ForeignKey('bank.accounts.account_number'))
    issued_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    cvv = db.Column(db.String(3))
    card_type = db.Column(db.String(10))
    card_status = db.Column(db.String(15))
    card_status_date = db.Column(db.DateTime)
    pin = db.Column(db.String(4))
    pin_change_date = db.Column(db.DateTime)

    account = db.relationship("Account",
                              primaryjoin="and_(Card.account_type==Account.account_type, "
                                          "Card.account_number==Account.account_number)",
                              )

    def __init__(self, account_type, account_number, card_type, card_number, issued_date, expiration_date, cvv):
        self.account_type = account_type
        self.account_number = account_number
        self.card_type = card_type
        self.card_number = card_number
        self.issued_date = parser.isoparse(issued_date)
        self.expiration_date = parser.isoparse(expiration_date)
        self.cvv = cvv
        self.card_status = CARD_STATUS['NOT_ACTIVE']

    def to_json(self):
        return {
            "cardType": self.card_type,
            "cardNumber": self.card_number,
            "issuedDate": self.issued_date,
            "expirationDate": self.expiration_date,
            "cardStatus": self.card_status,
            "cardStatusDate": self.card_status_date,
            "cvv": self.cvv,
            "account": {
                "accountType": self.account.account_type,
                "accountNumber": self.account.account_number,
                "customer": {
                    "id": self.account.customer.id,
                    "firstName": self.account.customer.first_name,
                    "lastName": self.account.customer.last_name,
                    "dateOfBirth": self.account.customer.date_of_birth,
                    "address": self.account.customer.address,
                    "email": self.account.customer.email
                },
                "accountOpenDate": self.account.open_date,
                "accountStatus": self.account.status,
                "accountClosedDate": self.account.close_date,
                "accountBalance": self.account.account_balance,
                "lastTransactionDate": self.account.last_transaction_date
            }
        }

    def validate(self):
        if not self.card_type in CARD_TYPE.values():
            return 'Invalid Card Type'
        #        if self.issued_date > datetime.now(tz=None):
        #            return 'Invalid Issued Date'
        if self.issued_date > self.expiration_date:
            return 'Issue Date cannot be later than expiration date'
        if re.match(CARD_NUMBER_FORMAT, self.card_number) is None:
            return 'Invalid Card Number. It must be 16 digits'
        if re.match(CVV_NUMBER_FORMAT, self.cvv) is None:
            return 'Invalid CVV Number. It must be 3 digits'

    def activate(self, pin):
        if self.card_status == CARD_STATUS['NOT_ACTIVE']:
            if re.match(PIN_NUMBER_FORMAT, pin) is None:
                return 'Invalid PIN Number. It must be 4 digits'
            self.pin = pin
            self.card_status = CARD_STATUS['ACTIVE']
            self.card_status_date = datetime.today()
        else:
            return 'Invalid Card Status'

    def lost(self):
        if self.card_status == CARD_STATUS['ACTIVE']:
            self.card_status = CARD_STATUS['LOST']
            self.card_status_date = datetime.today()
        else:
            return 'Card is not Active'

    def pinChange(self, old_pin, new_pin):
        if self.card_status == CARD_STATUS['ACTIVE']:
            if self.pin == old_pin:
                if re.match(PIN_NUMBER_FORMAT, new_pin) is None:
                    return 'Invalid Pin Number. It must be 4 digits'
                self.pin = new_pin
                self.card_status_date = datetime.today()
            else:
                return 'Pin does not match'
        else:
            return 'Card is not Active'


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = {'schema': 'bank'}
    transaction_id = db.Column(db.BigInteger, primary_key=True)
    transaction_date = db.Column(db.DateTime)
    account_type = db.Column(db.String(10), db.ForeignKey('bank.accounts.account_type'))
    account_number = db.Column(db.BigInteger, db.ForeignKey('bank.accounts.account_number'))
    transaction_mode = db.Column(db.String(10))
    transaction_amount = db.Column(db.Numeric(precision=15, scale=2))
    card_number = db.Column(db.String(16))
    description = db.Column(db.String(100))
    account_balance = db.Column(db.Numeric(precision=15, scale=2))

    account = db.relationship("Account",
                              primaryjoin="and_(Transaction.account_type==Account.account_type, "
                                          "Transaction.account_number==Account.account_number)",
                              )

    def __init__(self, transaction_date, account_type, account_number, transaction_mode, transaction_amount,
                 card_number,
                 description):
        self.transaction_date = transaction_date
        self.account_type = account_type
        self.account_number = account_number
        self.transaction_mode = transaction_mode
        self.transaction_amount = transaction_amount
        self.card_number = card_number
        self.description = description

    def to_json(self):
        return {
            "transactionId": self.transaction_id,
            "transactionDate": self.transaction_date,
            "transactionAmount": self.transaction_amount,
            "transactionMode": self.transaction_mode,
            "description": self.description,
            "cardNumber": self.card_number,
            "balance": self.balance,
            "account": {
                "accountType": self.account.account_type,
                "accountNumber": self.account.account_number,
            }
        }
