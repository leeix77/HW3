from flask import Flask
from flask import render_template, g
from flask import request
import sqlite3
import pandas as pd

app = Flask(__name__)

# when you try to access url like http://127.0.0.1:5000/, then run this hello_world method
@app.route("/") 
def hello_world():
    return "<h1>Hello world</h1>"

# when we try to access url http://127.0.0.1:5000/submit/, then run this method
@app.route("/submit/", methods=['POST', 'GET'])
def submit():
    get_message_db()
    if request.method == "GET":
        # if the user just visits the /submit/ url
        # render the submit.html template with no other parameters
        return render_template("submit.html")
    else: 
        # call insert_message()
        insert_message(request=request)
        # thank the user for their submission
        return render_template("submit.html", thanks=True)

# get_message_db() is used to handle creating the database of messages.
def get_message_db():
  # Check whether there is a database called message_db in the g attribute of the app. 
  # If not, then connect to that database. 
  try:
          return g.message_db
  except:
          g.message_db = sqlite3.connect("messages_db.sqlite")
          # Check whether a table called messages exists in message_db, and create it if not.
          # Give the table an id column (integer), a handle column (text), and a message column (text)
          cmd = '''
          CREATE TABLE IF NOT EXISTS messages(id INTEGER, handle TEXT, message TEXT);
          ''' 
          cursor = g.message_db.cursor()
          cursor.execute(cmd)
          return g.message_db


# insert_message() is used to handle inserting a user message into the database of messages
def insert_message(request):
    # Extract the message and the handle from request.
    message=request.form['message']
    handle=request.form['handle']
    # get the current number of rows in message_db
    cmd_id = f'''
    SELECT COUNT(*)
    FROM messages
    '''
    id = pd.read_sql_query(cmd_id, g.message_db).iloc[0,0]
    # insert the message (ID number, the handle, and the message) into the message database
    # set the ID number of a message equal to one plus the current number of rows
    cmd = f'''
    INSERT INTO messages(id, handle, message)
    VALUES('{id + 1}', '{handle}', '{message}');
    '''
    cursor = g.message_db.cursor()
    cursor.execute(cmd)
    # g.message_db.commit() is used to ensure that the row insertion has been saved
    g.message_db.commit()
    g.message_db.close()

# template view.html is used to display the messages extracted from random_messages()
@app.route("/view/")
def view():
    # call random_messages() to grab some random messages
    msg = random_messages(3)
    # pass the messages to view.html and render the view.html template
    return render_template("view.html", msg = msg)

# random_messages(n) is used to return a collection of n random messages from the message_db
def random_messages(n):
    conn = sqlite3.connect("messages_db.sqlite") 
    # SELECT * means select all columns, '{}' passes the parameter inside sql command
    # Select n random rows from a messages table
    cmd = \
    f"""
    SELECT * FROM messages ORDER BY RANDOM() LIMIT '{n}';
    """
    #read SQL query into the DataFrame
    df = pd.read_sql_query(cmd, conn)
    ##close the connection
    conn.close()
    return df

