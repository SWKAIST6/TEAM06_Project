from pymongo import MongoClient
# client = MongoClient ('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta

while True:
    jungler_name = input('이름을 입력해주세요: ')
    jungler_room = input('호실 번호를 입력해주세요 e.g. 101: ')
    jungler_enter = input('출입증 일련번호를 입력해주세요 e.g. D1111: ')

    db.junglers.insert_one({'name': jungler_name, 'room': jungler_room, 'enter_key': jungler_enter})

    print(jungler_room +'호 '+ jungler_name + ' jungler db에 추가되었습니다.\n')
