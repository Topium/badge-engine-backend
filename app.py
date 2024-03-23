from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_pyfile('settings.py')
mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/badges', methods=['GET'])
def get_data():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM badges_transform''')
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/badges/<int:id>', methods=['GET'])
def get_data_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM badges_transform WHERE id = %s''', (id,))
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