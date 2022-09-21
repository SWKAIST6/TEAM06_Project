from flask import Flask, render_template, jsonify, request, Blueprint
from pymongo import MongoClient  
from bson.objectid import ObjectId

### 내가 추가
from bson.json_util import dumps
from flask_socketio import SocketIO, join_room

### 내가 추가
from db import add_room, find_room, add_message, find_messages
import hashlib, datetime, jwt


app = Flask(__name__)
### 내가 추가
socketio = SocketIO(app, cors_allowed_origins="*")

# client = MongoClient ('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta  

@app.route('/')
def home():
   return render_template('form.html')

@app.route('/login')
def getLogin():
   return render_template('form.html')

@app.route('/register')
def getRegister():
   return render_template('signup.html')

@app.route('/main')
def getMain():
   return render_template('main.html')


# 본인인증 API
@app.route('/api/authentication', methods=['POST'])
def api_authentication():
   name_receive = request.form['name_give']
   room_receive = request.form['room_give']
   enter_receive = request.form['enter_give']
   
   user = {'name': name_receive, 'room': room_receive, 'enter_key': enter_receive}

   isJungler = db.junglers.find_one(user)
   isAlreadyUser = db.users.find_one({'name': name_receive})

   if isJungler is not None:
      if isAlreadyUser is None:
         return jsonify({'result': 'success'})
      else:
         return jsonify({'result': 'alreadyUser'})
   else:
      return jsonify({'result': 'fail'})

#회원가입 API
@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   name_receive = request.form['name_give']
   room_receive = request.form['room_give']

   result = db.users.find_one({'id': id_receive})

   if result is None:
      pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
      user = {'id': id_receive, 'pw': pw_hash, 'name': name_receive, 'room': room_receive}
      db.users.insert_one(user)
      duplicate = 0
   else:
      duplicate = 1

   return jsonify({'result': 'success', 'duplicate': duplicate})

#로그인 API
@app.route('/api/login', methods=['POST'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

   if result is not None:
      room_num = result['room']
      payload = {
            'id': id_receive,
            'room' : room_num,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)   
      }
      token = jwt.encode(payload, 'secret', algorithm='HS256')
      return jsonify({'result': 'success', 'token': token})
   else:
      return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

#게시글 작성
@app.route('/market', methods=['POST'])
def post_information():
   datetime_objected = datetime.datetime.now()
   datetime_spring = datetime_objected.strftime('%Y-%m-%d %H:%M:%S')
   title_receive = request.form['title_give']  # 클라이언트로부터 title 받기
   text_receive = request.form['text_give']  # 클라이언트로부터 text 받기
   category_receive = request.form['category_give']  # 클라이언트로부터 category 받기
   id_receive = request.form['id_give']
   room_receive = request.form['room_give']
   informations = {
      'datetime': datetime_spring,
      'title': title_receive,
      'text': text_receive,
      'category': category_receive,
      'id': id_receive,
      'room' : room_receive
   }
   # mongoDB에 데이터를 넣기
   db.informations.insert_one(informations)


   return jsonify({'result': 'success'})


#게시글 불러오기
@app.route('/market', methods=['GET'])
def show_information():
   data = list(db.informations.find())
   for information in data:
      information["_id"] = str(information["_id"])
   return render_template('main.html', informations=data)


#게시글 채팅창으로 넘어가기
@app.route('/exchange/<objectid>')
def url_generator(objectid):
   data = db.informations.find_one({'_id': ObjectId(objectid)})

   category = data['category']
   title = data['title'] 
   datetime = data['datetime'] 
   text = data['text']
   username = data['id']


   messages = list(find_messages(objectid))
   app.logger.info(type(objectid))


   return render_template('exchange.html',title=title, category=category, datetime=datetime,
      text=text, username=username, objectid = objectid, messages=messages )

#게시글 삭제하기
@app.route('/market/delete', methods=['POST'])
def delete_information():
   objectid_receive = ObjectId(request.form['objectid_give'])
   db.informations.delete_one({'_id': objectid_receive})
   return jsonify({'result': 'success'})

#게시글 수정하기
@app.route('/market/edit', methods=['POST'])
def edit_information():
   objectid_receive = ObjectId(request.form['objectid_give'])
   title_receive = request.form['title_give']
   text_receive = request.form['text_give']
   category_receive = request.form['category_give']
   db.informations.update_one(
      {'_id': objectid_receive},
      {'$set': {
         'title': title_receive,
         'text': text_receive,
         'category': category_receive
      }
      }
   )

   return jsonify({'result': 'success'})




### 내가 추가 - 소켓 시작
@socketio.on('join_room')
def handle_join_room_event(data):
   app.logger.info(f"{data['username']} has joined the room {data['room_id']}")
   join_room(data['room_id'])

   socketio.emit('join_room_announcement', data)


@socketio.on('send_message')
def handle_send_message(data):
   app.logger.info(f"{data['username']}, {data['room_id']}, {data['message']}")

   add_message(data['message'], data['username'],data['room_id'])

   socketio.emit('received_message', data)


if __name__ == '__main__':  
   app.run('0.0.0.0', port=5000, debug=True)
