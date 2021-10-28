from flask import make_response, jsonify, request, Blueprint

from Models.Models import Customer
from . import Database

bp = Blueprint('customers', __name__, url_prefix='/customers')


@bp.route("", methods=['GET'])
def getCustomers():
    """
        Fetch all the customers
    :return: List of customers
    :rtype: list
    """
    print(request.args)
    if request.args.get('last_name') is not None:
        last_name_query = request.args.get('last_name') + '%'
        customers = Database.MyBankDb.session.query(Customer).filter(Customer.last_name.like(last_name_query)).all()
    else:
        customers = Database.MyBankDb.session.query(Customer).all()

    response = []
    for customer in customers:
        response.append(customer.to_json())
    return make_response(jsonify(response), 200)


@bp.route("/<int:id>", methods=['GET'])
def getCustomer(id):
    if Database.MyBankDb.session.query(Customer.id).filter_by(id=id).scalar() is None:
        return make_response(jsonify({"message": "Customer Not Found"}), 404)

    customer = Database.MyBankDb.session.query(Customer).filter(Customer.id == id).first()
    response = customer.to_json()
    return make_response(jsonify(response), 200)


@bp.route("", methods=['POST'])
def addCustomer():
    data = request.get_json()
    customer = Customer(data['firstName'], data['lastName'], data['dateOfBirth'], data['address'], data['email'])
    if not customer.validate():
        return make_response(jsonify({"message": "Invalid Email Address"}), 400)
    Database.MyBankDb.session.add(customer)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Customer Added"}), 201)


@bp.route("/<int:id>", methods=['PUT'])
def appendCustomer(id):
    if Database.MyBankDb.session.query(Customer.id).filter_by(id=id).scalar() is None:
        return make_response(jsonify({"message": "Customer Not Found"}), 404)

    data = request.get_json()
    customer = Database.MyBankDb.session.query(Customer).filter(Customer.id == id).first()
    customer.first_name = data['firstName']
    customer.last_name = data['lastName']
    customer.date_of_birth = data['dateOfBirth']
    customer.address = data['address']
    customer.email = data['email']
    if not customer.validate():
        return make_response(jsonify({"message": "Invalid Email Address"}), 400)
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Customer Updated"}), 200)


@bp.route("/<int:id>", methods=['DELETE'])
def deleteCustomer(id):
    if Database.MyBankDb.session.query(Customer.id).filter_by(id=id).scalar() is None:
        return make_response(jsonify({"message": "Customer Not Found"}), 404)

    Database.MyBankDb.session.query(Customer).filter(Customer.id == id).delete()
    Database.MyBankDb.session.commit()
    return make_response(jsonify({"message": "Customer Deleted"}), 200)