import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from datetime import datetime
import logging, sys
from werkzeug.exceptions import abort

conn_count = 0

logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler("logfile.log")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count
    conn_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def post_count():
    connection = get_db_connection()
    posts = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    # posts = [dict(ix) for ix in posts]
    return posts[0]

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug("We have reached About Us Page!")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    logging.debug("{}, {} endpoint was reached".format(datetime.now(), request.path))
    return app.response_class(response=json.dumps({"result": "OK - healthy"}),mimetype='application/json')

@app.route('/metrics')
def metrics():
    logging.debug("{}, {} endpoint was reached".format(datetime.now(), request.path))
    return app.response_class(response=json.dumps({"db_connection_count": conn_count, "post_count" : post_count()}),mimetype='application/json')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
