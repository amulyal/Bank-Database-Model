from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
# connection string (host name, user id, password, database name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://amulya:**********@localhost:5432/MyBank'

MyBankDb = SQLAlchemy(app)
