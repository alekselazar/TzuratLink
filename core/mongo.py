from django.conf import settings
from mongoengine import connect
from django.conf import settings

def init_mongo():
    connect(
        db=settings.MONGODB_NAME,
        host=settings.MONGODB_HOST,
        uuidRepresentation="standard",
    )
