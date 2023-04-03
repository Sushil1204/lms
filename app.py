from crypt import methods
from datetime import datetime
from flask import Flask, flash, render_template, url_for, redirect, request
import requests 
from flask_mysqldb import MySQL
import MySQLdb
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField
import urllib

app = Flask(__name__)
app.secret_key = "sushilpundkar"


#mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sushil@1204'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'library'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_SQL_MODE'] = 'NO_ZERO_DATE,NO_ZERO_IN_DATE'

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

    print(request.method == 'POST' and form.validate())
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


#Book Routes
@app.route('/books')
def books():
    # Create MySQL cursor
    cur = mysql.connection.cursor()

    results = cur.execute("SELECT  id,title,author,total_quantity,available_quantity,rented_count FROM books")
    books  = cur.fetchall()

    if results > 0:
        return render_template('books.html', books=books)
    else:
        msg = "No Books Found"
        return render_template('books.html', warning=msg)

# Define Book Form
class BookForm(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])
    average_rating = FloatField(
        'Average Rating', [validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1, max=3)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField(
        'No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField(
        'No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField(
        'Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField(
        'Total No. of Books', [validators.NumberRange(min=1)])
   
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    # Get form data from request
    form = BookForm(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Check if book with same ID already exists
        result = cur.execute(
            "SELECT id FROM books WHERE id=%s", [form.id.data])
        book = cur.fetchone()
        if(book):
            error = 'Book with that ID already exists'
            return render_template('addBook.html', form=form, error=error)

        # Execute SQL Query
        cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            # When a book is first added, available_quantity = total_quantity
            form.total_quantity.data
        ])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("New Book Added", "success")

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    return render_template('addBook.html', form=form)


@app.route('/book-details/<string:id>')
def viewBook(id):
    
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    cur.close()
    # Render Template
    if result > 0:
        return render_template('bookDetails.html', book=book)
    else:
        msg = 'This Book Does Not Exist'
        return render_template('bookDetails.html', warning=msg)

    # Close DB Connection

class ImportBooks(Form):
    no_of_books = IntegerField('No. of Books*', [validators.NumberRange(min=1)])
    quantity_per_book = IntegerField(
        'Quantity Per Book*', [validators.NumberRange(min=1)])
    title = StringField(
        'Title', [validators.Optional(), validators.Length(min=2, max=255)])
    author = StringField(
        'Author(s)', [validators.Optional(), validators.Length(min=2, max=255)])
    isbn = StringField(
        'ISBN', [validators.Optional(), validators.Length(min=10, max=10)])
    publisher = StringField(
        'Publisher', [validators.Optional(), validators.Length(min=2, max=255)])


# Import Books from Frappe API
@app.route('/import_books', methods=['GET','POST'])
def importBooks():
    #get form data from request
    form = ImportBooks(request.form)

    #To handle Post request 
    if request.method == 'POST' and form.validate():
        # Create request structure    
        url  = 'https://frappe.io/api/method/frappe-library?'
        parameters = {'page': 1}

        if form.title.data:
            parameters['title'] = form.title.data
        if form.author.data:
            parameters['author'] = form.author.data
        if form.isbn.data:
            parameters['isbn'] = form.isbn.data
        if form.publisher.data:
            parameters['publisher'] = form.publisher.data

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # loops and requests
        books_imported = 0
        repeated_book_ids = []
        while (books_imported != form.no_of_books.data):
            r = requests.get(url + urllib.parse.urlencode(parameters))
            res = r.json()

            #break if message is empty
            if not res['message']:
                break

            for book in res['message']:
                result = cur.execute("SELECT id FROM books WHERE id=%s", [book['bookID']]) # check if book with same id already exists
                book_found = cur.fetchone()

                if(not book_found):
                     # Execute SQL Query
                    cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                        book['bookID'],
                        book['title'],
                        book['authors'],
                        book['average_rating'],
                        book['isbn'],
                        book['isbn13'],
                        book['language_code'],
                        book['  num_pages'],
                        book['ratings_count'],
                        book['text_reviews_count'],
                        book['publication_date'].format('YYYY-MM-DD'),
                        book['publisher'],
                        form.quantity_per_book.data,
                        # When a book is first added, available_quantity = total_quantity
                        form.quantity_per_book.data
                    ])
                    books_imported += 1
                    if books_imported == form.no_of_books.data:
                        break
                else:
                    repeated_book_ids.append(book['bookID'])
            parameters['page'] = parameters['page'] + 1

            # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success/Warning Message
        msg = str(books_imported) + "/" + \
            str(form.no_of_books.data) + " books have been imported. "
        msgType = 'success'
        if books_imported != form.no_of_books.data:
            msgType = 'warning'
            if len(repeated_book_ids) > 0:
                msg += str(len(repeated_book_ids)) + \
                    " books were found with already exisiting IDs."
            else:
                msg += str(form.no_of_books.data - books_imported) + \
                    " matching books were not found."

        flash(msg, msgType)

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    return render_template('importBooks.html', form=form)


#Edit book by ID
@app.route('/edit_book/<string:id>', methods=['GET','POST'])
def editBook(id):
      # Get form data from request
    form = BookForm(request.form)

    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # To get existing values of selected book
    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        # Check if book with same ID already exists (if ID field is being edited)
        if(form.id.data != id):
            result = cur.execute(
                "SELECT id FROM books WHERE id=%s", [form.id.data])
            book = cur.fetchone()
            if(book):
                error = 'Book with that ID already exists'
                return render_template('editBook.html', form=form, error=error, book=form.data)

        # Calculate new available_quantity (No. of books available to be rented)
        available_quantity = book['available_quantity'] + \
            (form.total_quantity.data - book['total_quantity'])

        # Execute SQL Query
        cur.execute("UPDATE books SET id=%s,title=%s,author=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s,total_quantity=%s,available_quantity=%s WHERE id=%s", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            available_quantity,
            id])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Updated", "success")

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    # To render edit book form
    return render_template('editBook.html', form=form, book=book)

# Delete Book by ID
@app.route('/delete_book/<string:id>', methods=['POST'])
def bookDelete(id):
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Since deleting parent row can cause a foreign key constraint to fail
    try:
        # Execute SQL Query
        cur.execute("DELETE FROM books WHERE id=%s", [id])

        # Commit to DB
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:

        print(e)
        # Flash Failure Message
        flash("Book could not be deleted", "danger")
        flash(str(e), "danger")

        # Redirect to show all members
        return redirect(url_for('books'))
    finally:
        # Close DB Connection
        cur.close()

    # Flash Success Message
    flash("Book Deleted", "success")

    # Redirect to show all books
    return redirect(url_for('books'))


# Transactions
@app.route('/transactions')
def transactions():
     # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM transactions")
    transactions = cur.fetchall()

    # To handle empty fields
    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"

    # Render Template
    if result > 0:
        return render_template('transactions.html', transactions=transactions)
    else:
        msg = 'No Transactions Found'
        return render_template('transactions.html', warning=msg)

    # Close DB Connection
    cur.close()

# Define Issue-Book-Form
class IssueBook(Form):
    book_id = SelectField('Book ID', choices=[])
    member_id = SelectField('Member ID', choices=[])
    per_day_fee = FloatField('Per Day Renting Fee', [
                             validators.NumberRange(min=1)])

#Issue Book
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    # Get form data from request
    form = IssueBook(request.form)

    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Create choices list for SelectField in form
    cur.execute("SELECT id, title FROM books")
    books = cur.fetchall()
    book_ids_list = []
    for book in books:
        t = (book['id'], book['title'])
        book_ids_list.append(t)

    cur.execute("SELECT id, name FROM members")
    members = cur.fetchall()
    member_ids_list = []
    for member in members:
        t = (member['id'], member['name'])
        member_ids_list.append(t)

    form.book_id.choices = book_ids_list
    form.member_id.choices = member_ids_list

    # To handle POST request to route
    if request.method == 'POST' and form.validate():

        # Get the no of books available to be rented
        cur.execute("SELECT available_quantity FROM books WHERE id=%s", [
                    form.book_id.data])
        result = cur.fetchone()
        available_quantity = result['available_quantity']

        # Check if book is available to be rented/issued
        if(available_quantity < 1):
            error = 'No copies of this book are availabe to be rented'
            return render_template('issueBook.html', form=form, error=error)

        # Execute SQL Query to create transaction
        cur.execute("INSERT INTO transactions (book_id,member_id,per_day_fee) VALUES (%s, %s, %s)", [
            form.book_id.data,
            form.member_id.data,
            form.per_day_fee.data,
        ])

        # Update available quantity, rented count of book
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity-1, rented_count=rented_count+1 WHERE id=%s", [form.book_id.data])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Issued", "success")

        # Redirect to show all transactions
        return redirect(url_for('transactions'))

    # To handle GET request to route
    return render_template('issueBook.html', form=form)

#return book form
class ReturnBook(Form):
    amount_paid = FloatField('Amount Paid', [validators.NumberRange(min=0)])

#Return book by trancation id
@app.route('/return_book/<string:transaction_id>', methods=['GET','POST'])
def returnBook(transaction_id):
    #Get the book data from the request
    form = ReturnBook(request.form)

    #mysql cursor
    cur = mysql.connection.cursor()

    # to get existing values of selected transaction
    cur.execute("SELECT * from transactions where id=%s",[transaction_id])
    transaction = cur.fetchone()

    #calculate billing
    date = datetime.now()
    diff = date - transaction['borrowed_on']
    diff = diff.days
    total_charge = diff * transaction['per_day_fee']

    #handling post request
    if request.method == 'POST' and form.validate():
        transaction_debt = total_charge - form.amount_paid.data

        # Check if bill amount exceets Rs.500
        cur.execute("SELECT outstanding_debt,amount_spent FROM members WHERE id=%s", [
                    transaction['member_id']])
        result = cur.fetchone()
        outstanding_debt = result['outstanding_debt']
        amount_spent = result['amount_spent']
        if(outstanding_debt + transaction_debt > 500):
            error = 'Outstanding debt cannot exceed Rs.500'
            return render_template('returnBook.html', form=form, error=error)

        # update return date, total charges and amount paid for this transacation 
        cur.execute("UPDATE transactions SET returned_on=%s,total_charge=%s,amount_paid=%s WHERE id=%s", [
            date,
            total_charge,
            form.amount_paid.data,
            transaction_id
        ])

        # Update outstanding_debt and amount_spent for this member
        cur.execute("UPDATE members SET outstanding_debt=%s, amount_spent=%s WHERE id=%s", [
            outstanding_debt+transaction_debt,
            amount_spent+form.amount_paid.data,
            transaction['member_id']
        ])

        # Update available_quantity for this book
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity+1 WHERE id=%s", [transaction['book_id']])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Returned", "success")

        # Redirect to show all transactions
        return redirect(url_for('transactions'))

    # To handle GET request to route
    return render_template('returnBook.html', form=form, total_charge=total_charge, difference=diff, transaction=transaction)


    
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)