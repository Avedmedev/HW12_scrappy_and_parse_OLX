from mongoengine import Document, StringField, connect


# https://www.olx.ua
class Flat(Document):
    title = StringField(required=True)
    price = StringField(required=True)
    location = StringField(required=True)
    square = StringField(required=True)
    meta = {'collection': 'flats'}




