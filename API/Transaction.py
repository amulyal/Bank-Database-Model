from flask import request, make_response, jsonify, Blueprint

from API import Database, Customer, Account
from Models.Models import Card, Account
from Repository.transaction_manager import TransactionManager
from datetime import date
from dateutil import parser

bp_transactions = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp_transactions.route("", methods=['GET'])
def get_transactions():
    # convert to timestamp
    transaction_date = date.now()
    if request.args.get('transaction_date') is not None:
        transaction_date = parser.parse(request.args.get('transaction_date'))

    transactions = TransactionManager.getTransactionByDate(transaction_date)
    response = []
    for transaction in transactions:
        response.append(transaction.to_json())
    return make_response(jsonify(response), 200)


@bp_transactions.route("", methods=['POST'])
def post_transactions():
    data = request.get_json()
    message = TransactionManager.post(data['accountType'], data['accountNumber'], data['transactionMode'],
                                      data['transactionAmount'], data['cardNumber'], data['description'])
    if not message is None:
        return make_response(jsonify({"Error": message}))
    return make_response(jsonify({"Message": "Transaction posted"}), 200)
