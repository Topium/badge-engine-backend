from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from flask_cors import CORS
from passlib.hash import pbkdf2_sha512

app = Flask(__name__)
CORS(app, origins='http://localhost:5173', support_credentials=True)
app.config.from_pyfile('settings.py')
app.config["JWT_SECRET_KEY"] = 'verysecret'
mysql = MySQL(app)
jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/token', methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    cur = mysql.connection.cursor()
    cur.execute('''\
        SELECT * FROM `badges_users`\
        WHERE username = %s;''', (username,))
    if cur.rowcount == 0:
        cur.close()
        response = jsonify({"msg": "Wrong password or username"})
        return response, 401
    
    data = cur.fetchall()
    cur.close()
    db_password = data[0][2]

    if pbkdf2_sha512.verify(password, db_password):
        access_token = create_access_token(identity=username)
        response = jsonify({"username": username, "access_token":access_token})
        return response
    else:
        response = jsonify({"msg": "Wrong password or username"})
        return response, 401

@app.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/badges', methods=['GET'])
@jwt_required()
def get_data():
    user = get_jwt_identity()
    print('jwt identity', user)
    cur = mysql.connection.cursor()
    cur.execute('''\
        SELECT b.id, b.badge_name, bt.scale, bt.x_pos, bt.y_pos, bt.badge_url, bu.username\
        FROM badges AS b\
        INNER JOIN badges_transform AS bt\
        ON b.transform_id = bt.id\
        INNER JOIN badges_users AS bu\
        ON b.user_id = bu.id\
        WHERE bu.username = %s''', (user,))
    if cur.rowcount == 0:
        response = jsonify({"msg": "No badges found"})
        return response, 400

    row_headers=[x[0] for x in cur.description]
    data = cur.fetchall()
    cur.close()
    json_data=[]
    for result in data:
            json_data.append(dict(zip(row_headers,result)))
    return jsonify(json_data)

@app.route('/badges/<int:id>', methods=['GET'])
@jwt_required()
def get_data_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('''\
        SELECT * FROM badges\
        INNER JOIN badges_transform\
        ON badges.transform_id = badges_transform.id\
        WHERE badges.id = %s''', (id,))
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/data', methods=['POST'])
def add_data():
    cur = mysql.connection.cursor()
    name = request.json['name']
    age = request.json['age']
    cur.execute('''INSERT INTO table_name (name, age) VALUES (%s, %s)''', (name, age))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Data added successfully'})

@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    cur = mysql.connection.cursor()
    name = request.json['name']
    age = request.json['age']
    cur.execute('''UPDATE table_name SET name = %s, age = %s WHERE id = %s''', (name, age, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Data updated successfully'})

@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    cur = mysql.connection.cursor()
    cur.execute('''DELETE FROM table_name WHERE id = %s''', (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == "__main__":
    app.run(debug=True)