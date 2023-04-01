from flask import Flask, render_template
from flask_mysqldb import MySQL
import MySQLdb



app = Flask(__name__)

#mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sushil@1204'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'librarydb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialise MYSQL
mysql = MySQL(app)


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
  app.run(debug=True)