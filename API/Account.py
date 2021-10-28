from flask import make_response, jsonify, request, Blueprint

from API import Database
from Models.Models import Account, Customer
from Repository.account_repository import AccountRepository

bp = Blueprint('accounts', __name__, url_prefix='/accounts')


@bp.route("", methods=['GET'])
def getAccounts():
    if request.args.get('last_name') is not None:
        last_name_query = request.args.get('last_name') + '%'
        accounts = Database.MyBankDb.session.query(Account).join(Customer).filter(
            Customer.last_name.like(last_name_query)).all()
    else:
        accounts = Database.MyBankDb.session.query(Account).all()

    response = []
    for account in accounts:
        response.append(Account.to_json(account))
    return make_response(jsonify(response), 200)


@bp.route("<string:account_type>/<int:account_number>", methods=['GET'])
def getAccount(account_type, account_number):
    account_type = account_type.upper()
    if AccountRepository.checkAccountExists(account_type, account_number) == False:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    account = Database.MyBankDb.session.query(Account).filter(Account.account_type == account_type,
                                                                             Account.account_number == account_number).first()
    response = account.to_json()
    return make_response(jsonify(response), 200)


@bp.route("", methods=['POST'])
def addAccount():
    data = request.get_json()
    account = Account(data['accountType'], data['customerId'], data['accountOpenDate'], data['accountStatus'])
    Database.MyBankDb.session.add(account)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Account Added"}), 201)


@bp.route("/<int:account_number>", methods=['PUT'])
def appendAccount(account_number):
    if Database.MyBankDb.session.query(Account.account_number).filter_by(
            account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    data = request.get_json()
    account = Database.MyBankDb.session.query(Account).filter(Account.account_number == account_number).first()
    account.account_type = data['accountType']
    account.open_date = data['accountOpenDate']
    account.status = data['accountStatus']
    account.account_balance = data['accountBalance']
    account.close_date = data['accountCloseDate']
    account.last_transaction_date = data['LastTransactionDate']
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Account Updated"}), 200)


@bp.route("/<int:account_number>", methods=['DELETE'])
def deleteAccount(account_number):
    if Database.MyBankDb.session.query(Account.account_number).filter_by(
            account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    Database.MyBankDb.session.query(Account).filter(Account.account_number == account_number).delete()
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Account Deleted"}), 200)
