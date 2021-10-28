from Models.Models import Account
from API import Customer, Database, Account, Card, Transaction

# from Models.Account import Account

app = Database.app


def register_routes():
    app.register_blueprint(Customer.bp)
    app.register_blueprint(Account.bp)
    app.register_blueprint(Card.bp_cards)
    app.register_blueprint(Card.bp_accounts)
    app.register_blueprint(Transaction.bp_transactions)


register_routes()
print(app.url_map)
app.run(port=6000)
