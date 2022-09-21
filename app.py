from flask import Flask, render_template, jsonify, request, Blueprint
from pymongo import MongoClient  
import hashlib, datetime, jwt


app = Flask(__name__)

client = MongoClient('localhost', 27017) 
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


@app.route('/api/authentication', methods=['POST'])
def api_authentication():
   name_receive = request.form['name_give']
   room_receive = request.form['room_give']
   enter_receive = request.form['enter_give']
   
   print(name_receive)
   print(room_receive)
   print(enter_receive)
   
   user = {'name': name_receive, 'room': room_receive, 'enter_key': enter_receive}

   result = db.junglers.find_one(user)

   if result is not None:
      return jsonify({'result': 'success'})
   else:
      return jsonify({'result': 'fail'})

@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   name_receive = request.form['name_give']
   room_receive = request.form['room_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   user = {'id': id_receive, 'pw': pw_hash, 'name': name_receive, 'room': room_receive}

   db.users.insert_one(user)

   return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

   if result is not None:
      payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5)   
      }
      token = jwt.encode(payload, 'secret', algorithm='HS256')
      return jsonify({'result': 'success', 'token': token})
   else:
      return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/market', methods=['POST'])
def post_information():
   datetime_objected = datetime.datetime.now()
   datetime_spring = datetime_objected.strftime('%Y-%m-%d %H:%M:%S')
   title_receive = request.form['title_give']  # 클라이언트로부터 title 받기
   text_receive = request.form['text_give']  # 클라이언트로부터 text 받기
   category_receive = request.form['category_give']  # 클라이언트로부터 category 받기

   informations = list(db.informations.find({}, {'_id': 0}))
   history = len(informations)
   post_numbers = []
   for i in range(history):
      post_numbers.append(i)
   if len(post_numbers) == 0:
      max_post_number = 0
   else:
      max_post_number = max(post_numbers, default=0)+1

   informations = {
      'postnumber': max_post_number,
      'datetime': datetime_spring,
      'title': title_receive,
      'text': text_receive,
      'category': category_receive
   }

   # mongoDB에 데이터를 넣기
   db.informations.insert_one(informations)
   return jsonify({'result': 'success'})


@app.route('/market', methods=['GET'])
def show_information():
   data = list(db.informations.find({}, {'_id': False}))
   return render_template('main.html', informations=data)


@app.route('/exchange/<postnumber>')
def url_generator(postnumber):
   data = list(db.informations.find({}, {'_id': False}))
   return render_template('exchange.html', informations=data[int(postnumber)])



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
