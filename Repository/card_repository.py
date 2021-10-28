from API import Database
from Models.Models import Card


class CardRepository:

    @staticmethod
    def checkCardExists(card_number):
        if Database.MyBankDb.session.query(Card.card_number).filter_by(Card.card_number == card_number).scalar() is None:
            return False
        else:
            return True

    @staticmethod
    def get_card(card_number):
        return Database.MyBankDb.session.query(Card).filter(Card.card_number == card_number).first()
