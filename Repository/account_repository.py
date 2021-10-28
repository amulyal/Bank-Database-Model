from API import Database
from Models.Models import Account


class AccountRepository:

    @staticmethod
    def checkAccountExists(account_type, account_number):
        if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                             account_number=account_number).scalar() is None:
            return False
        else:
            return True

    @staticmethod
    def getAccount(account_type, account_number):
        return Database.MyBankDb.session.query(Account).filter(Account.account_type == account_type,
                                                               Account.account_number == account_number).first()
