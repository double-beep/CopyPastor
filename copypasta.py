import sqlite3
from html import unescape

from flask import Flask, render_template, request, jsonify, g
from datetime import datetime

app = Flask(__name__)
DATABASE = 'copypastorDB.db'


@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return render_template('error.html', message="Sorry, that page doesn't exist ..."), 404


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return render_template('error.html', message="Umph! Something bad happened, we'll look into it. Thanks ..."), 500


@app.route("/posts/create", methods=['POST'])
def store_post():
    try:
        date_one = request.form["date_one"]
        date_two = request.form["date_two"]
        if date_one < date_two:
            return jsonify({"status": "failure", "message": "Error - Plagiarized post created earlier"}), 400
        data = (request.form["url_one"], request.form["url_two"], request.form["title_one"],
                request.form["title_two"], date_one, date_two, request.form["body_one"], request.form["body_two"])
        post_id = store_data(data)
    except KeyError as e:
        return jsonify({"status": "failure", "message": "Error - Missing argument {}".format(e.args[0])}), 400
    return jsonify({"status": "success", "post_id": post_id})


@app.route("/feedback/create", methods=['POST'])
def store_feedback():
    try:
        data = (request.form["post_id"], request.form["feedback_type"], request.form["user"], request.form["link"])
        status = store_data(data)
        if status:
            return jsonify({"status": "failure", "message": status}), 400
    except KeyError as e:
        return jsonify({"status": "failure", "message": "Error - Missing argument {}".format(e.args[0])}), 400
    return jsonify({"status": "success", "message": "feedback stored"})


@app.route("/posts/<int:post_id>", methods=['GET'])
def get_post(post_id):
    data = retrieve_data(post_id)
    if data is None:
        return render_template('error.html', message="Sorry, that page doesn't exist ..."), 404
    try:
        return render_template('render.html', url_one=data["url_one"], url_two=data["url_two"],
                               title_one=unescape(data["title_one"]), title_two=unescape(data["title_two"]),
                               date_one=datetime.fromtimestamp(float(data["date_one"])),
                               date_two=datetime.fromtimestamp(float(data["date_two"])),
                               body_one=get_body(data["body_one"]), body_two=get_body(data["body_two"]))
    except KeyError as e:
        print(e)
        return render_template('error.html', message="Sorry, the post has been deleted ..."), 410


def get_body(body):
    return unescape(body).split("\r\n")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    db = get_db()
    cur = db.cursor()
    with app.open_resource('schema.sql', mode='r') as f:
        cur.executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


@app.teardown_appcontext
def close_connection(exception):
    if exception:
        print(exception)
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def store_data(data):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO posts "
                    "(url_one, url_two, title_one, title_two, date_one, date_two, body_one, body_two) "
                    "VALUES (?,?,?,?,?,?,?,?);", data)
        cur.execute("SELECT last_insert_rowid();")
        post_id = cur.fetchone()[0]
        db.commit()
        return post_id


def retrieve_data(post_id):
    with app.app_context():
        cur = get_db().cursor()
        cur.execute("SELECT url_one, url_two, title_one, title_two, date_one, date_two, body_one, body_two FROM posts "
                    "WHERE post_id=?;", (post_id,))
        row = cur.fetchone()
        if row is None:
            return None
        data = {i: j for i, j in
                zip(('url_one', 'url_two', 'title_one', 'title_two', 'date_one', 'date_two', 'body_one', 'body_two'),
                    row)}
        return data

