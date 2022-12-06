# flask, flask-jwt-extended, pymysql 라이브러리 설치
from flask import Flask, render_template, request, jsonify, redirect, url_for
# local sql 연결
import pymysql
# 유효기간 및 작성 날짜 정보
from datetime import datetime, timedelta
# client 통신 할때 형식 jsonquery
import json
# 토큰 발행
import jwt


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'

# 특정데이터 테스트
# db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
# curs = db.cursor()
#
# email_receive = 'aaaa'
#
# sql = """
# 	SELECT *
# 		FROM users u
# 		WHERE u.email = %s
# 	"""
#
# curs.execute(sql, email_receive)
#
# users_result = curs.fetchall()
# print(users_result[0])
#
# json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
# db.commit()
# db.close()

@app.route('/')
def home():
	return render_template('index.html')


@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/log_in', methods=['POST'])
def log_in():
	email_receive = request.form["email_give"]
	password_receive = request.form["password_give"]
	# print(email_receive)
	# print(password_receive)

	db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
	curs = db.cursor()

	sql = """
		SELECT u.email, u.pw
		FROM users u
		where u.email = %s
		"""

	curs.execute(sql, email_receive)

	users_result = curs.fetchall()
	# print(users_result[0][1] != password_receive)

	json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
	db.commit()
	db.close()

	if users_result[0][1] != password_receive:
		msg = "비밀번호가 일치하지 않습니다. 다시 로그인해주세요."
		return jsonify({'result': 'fail', 'msg': msg})
	else:
		# 토큰 발행, id, payload, 시크릿키가 필요
		payload = {
			'id': email_receive,
			'exp': datetime.utcnow() + timedelta(seconds=60*60*24)
		}
		token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
		# print(token)
		return jsonify({'result': 'success', 'token': token})

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/users/sign_up', methods=['POST'])
def save_users_info():
	email_receive = request.form['email_give']
	password_receive = request.form['password_give']
	# password2_receive = request.form['password2_give']
	name_receive = request.form['name_give']

	file = request.files["file_give"]
	print(file)
	extension = file.filename.split('.')[-1]
	today = datetime.now()
	mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
	filename = f'file-{mytime}'
	save_to = f'{filename}.{extension}'
	file.save(f'static/images/{save_to}')
	print(save_to)

	db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
	curs = db.cursor()

	sql = """
		insert into users (email, pw, name, regrate, filename)
         values (%s,%s,%s,%s,%s)
		"""

	curs.execute(sql, (email_receive, password_receive, name_receive, mytime, save_to))

	users_result = curs.fetchall()
	# print(users_result[0][1] != password_receive)

	json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
	db.commit()
	db.close()

	return jsonify({"result":"success", 'msg':'회원가입 완료!'})

# @app.route('/mypage')
# def mypage():
# 	token_receive = request.cookies.get('mytoken')
#
# 	try:
# 		jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
# 		return render_template('mypage.html')
# 	except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# 		return redirect(url_for("login", msg="로그인을 먼저 진행해주세요."))

# @app.route('/mypage/user', methods=['GET'])
# def mypage_info():
# 	token_receive = request.cookies.get('mytoken')
#
# 	try:
# 		payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#
# 		db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
# 		curs = db.cursor()
#
# 		sql = """
# 			SELECT *
# 			FROM users u
# 			WHERE u.email = %s
# 			"""
#
# 		curs.execute(sql, payload["id"])
#
# 		users_result = curs.fetchall()
# 		# print(users_result[0][1] != password_receive)
#
# 		json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
# 		db.commit()
# 		db.close()
# 		return jsonify({'result': 'success', 'user_info': users_result[0]})
# 	except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
# 		return redirect(url_for("login", msg="로그인을 먼저 진행해주세요."))

@app.route('/user_only', methods=['POST'])
def user_only():
	token_receive = request.cookies.get('mytoken')
	print(token_receive)

	try:
		payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
		msg = payload['id'] + '님은 게시물을 작성하실 수 있습니다.'
		# db 접근
		return jsonify({'msg': msg})
	except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
		return jsonify({'msg': 'User Only Access!!!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)