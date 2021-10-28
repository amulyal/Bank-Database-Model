from flask import request, make_response, jsonify, Blueprint

from API import Database, Customer
from Models.Models import Card, Account

bp_cards = Blueprint('cards', __name__, url_prefix='/cards')
bp_accounts = Blueprint('card-accounts', __name__, url_prefix='/accounts')


@bp_cards.route("", methods=['GET'])
def getCards():
    # if request.args.get('last_name') is not None:
    # last_name_query = request.args.get('last_name') + '%'
    # cards = Database.MyBankDb.session.query(Card).join(Account,primaryjoin="and_(Card.account_type==Account.account_type, ""Card.account_number==Account.account_number)").join(Customer).filter(Card.last_name.like(last_name_query)).all()
    # else:
    # cards = Database.MyBankDb.session.query(Card).all()

    cards = Database.MyBankDb.session.query(Card).all()
    response = []
    for card in cards:
        response.append(
            {
                "cardType": card.card_type,
                "cardNumber": card.card_number,
                "issuedDate": card.issued_date,
                "expirationDate": card.expiration_date,
                "cardStatus": card.card_status,
                "cardStatusDate": card.card_status_date,
                "cvv": card.cvv,
                "account": {
                    "accountType": card.account.account_type,
                    "accountNumber": card.account.account_number,
                    "accountOpenDate": card.account.open_date,
                    "accountStatus": card.account.status,
                    "accountClosedDate": card.account.close_date,
                    "accountBalance": card.account.account_balance,
                    "lastTransactionDate": card.account.last_transaction_date,
                    "customer": {
                        "id": card.account.customer.id,
                        "firstName": card.account.customer.first_name,
                        "lastName": card.account.customer.last_name,
                        "dateOfBirth": card.account.customer.date_of_birth,
                        "address": card.account.customer.address,
                        "email": card.account.customer.email
                    }
                }
            })
    return make_response(jsonify(response), 200)


@bp_accounts.route("/<string:account_type>/<int:account_number>/cards", methods=['GET'])
def getAccountCards(account_type, account_number):
    account_type = account_type.upper()
    if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                         account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)
    cards = Database.MyBankDb.session.query(Card).filter(Card.account_type == account_type,
                                                         Card.account_number == account_number).all()

    response = []
    for card in cards:
        response.append(Card.to_json(card))
    return make_response(jsonify(response), 200)


@bp_accounts.route("/<string:account_type>/<int:account_number>/cards", methods=['POST'])
def issueCard(account_type, account_number):
    account_type = account_type.upper()
    if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                         account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    data = request.get_json()
    card = Card(account_type, account_number, data['cardType'], data['cardNumber'], data['issuedDate'],
                data['expirationDate'], data['cvv'])
    message = card.validate()
    if not message is None:
        return make_response(jsonify({"message": message}), 400)

    Database.MyBankDb.session.add(card)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Card Issued"}), 201)


@bp_accounts.route("/<string:account_type>/<int:account_number>/cards/<string:card_number>/card-activation",
                   methods=['POST'])
def activateCard(account_type, account_number, card_number):
    account_type = account_type.upper()
    data = request.get_json()
    if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                         account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)
    if Database.MyBankDb.session.query(Card.card_number).filter_by(card_number=card_number).scalar() is None:
        return make_response(jsonify({"message": "Card Not Found"}), 404)
    card = Database.MyBankDb.session.query(Card).filter(Card.card_number == card_number).first()
    message = card.activate(data['pin'])
    if message is not None:
        return make_response(jsonify({"Error": message}), 400)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"Message": "Card Activated"}), 200)


@bp_accounts.route("/<string:account_type>/<int:account_number>/cards/<string:card_number>/card-lost",
                   methods=['POST'])
def lostCard(account_type, account_number, card_number):
    account_type = account_type.upper()
    if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                         account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    if Database.MyBankDb.session.query(Card.card_number).filter_by(card_number=card_number).scalar() is None:
        return make_response(jsonify({"message": "Card Not Found"}), 404)
    card = Database.MyBankDb.session.query(Card).filter(Card.card_number == card_number).first()
    message = card.lost()

    if message is not None:
        return make_response(jsonify({"Error": message}), 400)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"Message": "Card is Lost"}), 200)


@bp_accounts.route("/<string:account_type>/<int:account_number>/cards/<string:card_number>/reset-pin",
                   methods=['POST'])
def changePin(account_type, account_number, card_number):
    account_type = account_type.upper()
    data = request.get_json()
    if Database.MyBankDb.session.query(Account.account_number).filter_by(account_type=account_type,
                                                                         account_number=account_number).scalar() is None:
        return make_response(jsonify({"message": "Account Not Found"}), 404)

    if Database.MyBankDb.session.query(Card.card_number).filter_by(card_number=card_number).scalar() is None:
        return make_response(jsonify({"message": "Card Not Found"}), 404)
    card = Database.MyBankDb.session.query(Card).filter(Card.card_number == card_number).first()
    message = card.pinChange(data['pin'], data['newPin'])

    if message is not None:
        return make_response(jsonify({"Error": message}), 400)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"Message": "Pin is changed"}), 200)