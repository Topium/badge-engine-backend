from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.config["JWT_SECRET_KEY"] = 'verysecret'
mysql = MySQL(app)
jwt = JWTManager(app)
CORS(app, support_credentials=True)

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
        WHERE username = %s AND password = %s''', (username, password))
    if cur.rowcount == 0:
        response = jsonify({"msg": "Wrong email or password"})
        return response, 401

    access_token = create_access_token(identity=username)
    response = jsonify({"username": username, "access_token":access_token})
    return response

@app.route('/badges', methods=['GET'])
def get_data():
    cur = mysql.connection.cursor()
    cur.execute('''\
        SELECT * FROM badges\
        INNER JOIN badges_transform\
        ON badges.id = badges_transform.badge_id;''')
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
def get_data_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('''\
        SELECT * FROM badges\
        INNER JOIN badges_transform\
        ON badges.id = badges_transform.badge_id\
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