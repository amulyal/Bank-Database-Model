from Models.Models import Account, Transaction
from API import Database
from datetime import datetime
from Repository.account_repository import AccountRepository
from Repository.card_repository import CardRepository

TRANSACTION_MODE = {'CREDIT': 'CREDIT',
                    'DEBIT': 'DEBIT'}

MIN_AMOUNT = 100
MAX_AMOUNT = 500000


class TransactionManager:

    @staticmethod
    def post(account_type, account_number, transaction_mode, transaction_amount, card_number, description):
        balance = 0
        if not AccountRepository.checkAccountExists(account_type=account_type, account_number=account_number):
            return "Account Does Not Exist"

        account = AccountRepository.getAccount(account_type=account_type, account_number=account_number)

        if account.status == "Closed":
            return "Account Closed"

        if not transaction_mode in TRANSACTION_MODE.values():
            return 'Invalid Transaction Mode'

        if transaction_amount < MIN_AMOUNT or transaction_amount > MAX_AMOUNT:
            return "Amount is out of acceptable range"

        if not card_number is None and CardRepository.checkCardExists(card_number=card_number) == False:
            return "Card Does not exists"

        if not account.account_balance is None:
            balance = account.account_balance
        if transaction_mode == TRANSACTION_MODE['CREDIT']:
            balance += transaction_amount
        else:
            balance -= transaction_amount

        account.last_transaction_date = datetime.now()

        transaction = Transaction(datetime.now(), account_type, account_number, transaction_mode, transaction_amount,
                                  card_number, description)

        transaction.account_balance = balance
        account.account_balance = balance

        Database.MyBankDb.session.add(transaction)

        Database.MyBankDb.session.commit()

    @staticmethod
    def getTransactionByDate(transaction_date):
        return Database.MyBankDb.session.query(Transaction).filter(Transaction.transaction_date == transaction_date).all()
