from flask import Flask, flash, render_template, url_for, redirect, request
import requests 
from flask_mysqldb import MySQL
import MySQLdb
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField



app = Flask(__name__)
app.secret_key = "sushilpundkar"

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

        # Flash Success Message
        flash("New Member Added", "success")

        # Redirect to show all members
        return redirect(url_for('members'))    
    return render_template('addMember.html', form=form)

# Delete Member by ID
@app.route('/delete_member/<string:id>', methods=['POST'])
def delete_member(id):

    # Create MySQLCursor
    cur = mysql.connection.cursor()
    # Since deleting parent row can cause a foreign key constraint to fail
    try:
        # Execute SQL Query
        cur.execute("DELETE FROM members WHERE id=%s", [id])

        # Commit to DB
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        # Flash Failure Message
        flash("Member could not be deleted", "danger")
        flash(str(e), "danger")

        # Redirect to show all members
        return redirect(url_for('members'))
    finally:
        # Close DB Connection
        cur.close()

    # Flash Success Message
    flash("Member Deleted", "success")

    # Redirect to show all members
    return redirect(url_for('members'))

# Edit Member by ID
@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
def edit_member(id):
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
            "UPDATE members SET name=%s, email=%s WHERE id=%s", (name, email, id))

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Member Updated", "success")

        # Redirect to show all members
        return redirect(url_for('members'))

           # To handle GET request to route

    # To get existing field values of selected member
    cur2 = mysql.connection.cursor()
    result = cur2.execute("SELECT name,email FROM members WHERE id=%s", [id])
    member = cur2.fetchone()
    # To render edit member form
    return render_template('editMember.html', form=form, member=member)

if __name__ == '__main__':
    app.run(debug=True)