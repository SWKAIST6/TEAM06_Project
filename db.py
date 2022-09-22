
from datetime import datetime
from pymongo import MongoClient

client = MongoClient ('localhost', 27017)
# client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta

room_collection = db.room
message_collection = db.message


def add_room(room_id, admin_user):
    room_collection.insert_one({'room_id':room_id, 'admin_user':admin_user})


def find_room(room_id):
    return room_collection.find_one({'room_id':room_id})

def add_message(content, user, roomId):
    message_collection.insert_one({'content':content, 'created':datetime.now(),
        'user':user, 'room_id':roomId})


def find_messages(roomId):
    return message_collection.find({
        'room_id':roomId
    }).sort("created",-1).limit(3)



