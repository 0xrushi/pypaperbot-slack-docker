from flask import Flask, jsonify, request
import json
import mysql.connector

app = Flask(__name__)

config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'db_tasks'
    }

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    cur.execute("SELECT * FROM db_tasks.tasks")
    row_headers=[x[0] for x in cur.description] #this will extract row headers
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return json.dumps(json_data)

@app.route('/api/task', methods=['POST'])
def add_task():
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    title = request.get_json()['title']
    cur.execute("INSERT INTO db_tasks.tasks (title) VALUES ('" + str(title) + "')")
    connection.commit()
    result = {'title':title}

    return jsonify({"result": result})

@app.route("/api/task/<id>", methods=['PUT'])
def update_task(id):
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    title = request.get_json()['title']
    
    cur.execute("UPDATE db_tasks.tasks SET title = '" + str(title) + "' where id = " + id)
    connection.commit()

    result = {"title": title}

    return jsonify({"result": result})

@app.route("/api/task/<id>", methods=['DELETE'])
def delete_task(id):
    connection = mysql.connector.connect(**config)
    cur = connection.cursor()
    response = cur.execute("DELETE FROM db_tasks.tasks where id = " + id)
    connection.commit()

    if response > 0:
        result = {'message' : 'record deleted'}
    else:
        result = {'message' : 'no record found'}
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
