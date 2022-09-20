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

@app.route('/api/register', methods=['post'])
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



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
