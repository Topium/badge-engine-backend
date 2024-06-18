import os
import pymysql 

from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from flask_cors import CORS
from passlib.hash import pbkdf2_sha512
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
host = os.environ.get('MYSQL_HOST')
user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DB')
cors_origin = os.environ.get('CORS_ORIGIN')

db = pymysql.connect(host=host, user=user, password=password, database=database)

app = Flask(__name__)
CORS(app, origins=cors_origin, support_credentials=True)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)

# Check for extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def root():
    print(Flask.url_for(app, endpoint='root', _external=True))
    return 'Hello, World!'

@app.route('/token', methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    cur = db.cursor()
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
    cur = db.cursor()
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
    cur = db.cursor()
    cur.execute('''\
        SELECT * FROM badges\
        INNER JOIN badges_transform\
        ON badges.transform_id = badges_transform.id\
        WHERE badges.id = %s''', (id,))
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/badges', methods=['POST'])
@jwt_required()
def add_data():
    print('add data')
    print(request.form)
    badge_name = request.form['badge_name']
    scale = request.form['scale']
    x_pos = request.form['x_pos']
    y_pos = request.form['y_pos']
    # badge_url = request.form['badge_url']
    print('name', badge_name, ' x', x_pos, ' y', y_pos, ' scale', scale)
    user = get_jwt_identity()

    cur = db.cursor()
    cur.execute('''SELECT id FROM badges_users WHERE username = %s;''', (user,))
    if cur.rowcount == 0:
        cur.close()
        response = jsonify({"msg": "Username error"})
        return response, 401
    
    data = cur.fetchall()
    user_id = data[0][0]
    print('user_id', user_id)
    cur.close()

    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        return jsonify({'message': 'No file'})
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        print('No selected file')
        return jsonify({'message': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_url = Flask.url_for(app, endpoint='root', _external=True) + local_path
        file.save(local_path)
        print(file_url)

    return jsonify({'message': 'TODO: Badge added successfully'})

@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    cur = db.cursor()
    name = request.json['name']
    age = request.json['age']
    cur.execute('''UPDATE table_name SET name = %s, age = %s WHERE id = %s''', (name, age, id))
    db.commit()
    cur.close()
    return jsonify({'message': 'Data updated successfully'})

@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    cur = db.cursor()
    cur.execute('''DELETE FROM table_name WHERE id = %s''', (id,))
    db.commit()
    cur.close()
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == "__main__":
    app.run(debug=True)