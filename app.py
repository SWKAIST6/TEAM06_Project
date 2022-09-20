from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient     
import hashlib
      
client = MongoClient('localhost', 27017)  
db = client.dbsparta                    

app = Flask(__name__)

## URL 별로 함수명이 같거나,
## route('/') 등의 주h소가 같으면 안됩니다.

@app.route('/')
def home():
   return render_template('signup.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})



@app.route('/api/chat', methods=['GET','POST'])
def api_chat():
   pass




if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)