from flask import Flask, flash, render_template, url_for, redirect, request
import requests 
from flask_mysqldb import MySQL
import MySQLdb
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField



app = Flask(__name__)

#mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sushil@1204'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'library'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialise MYSQL
mysql = MySQL(app)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/members")
def members():
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM members")
    members = cur.fetchall()

    # Render Template
    if result > 0:
        return render_template('members.html', members=members)
    else:
        msg = 'No Members Found'
        return render_template('members.html', warning=msg)

    # Close DB Connection
    cur.close()

class MemberForm(Form):
    name = StringField('Name', [validators.length(min=3, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])

@app.route("/add-member", methods=['GET', 'POST'])
def add_member():
    # Get form data from request
    form = MemberForm(request.form)

     # To handle POST request to route
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

         # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Execute SQL Query
        cur.execute(
            "INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()
        
        return redirect(url_for('members'))    
    return render_template('addMember.html', form=form)
if __name__ == '__main__':
  app.run(debug=True)