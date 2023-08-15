from flask import Flask, render_template 
from flask_sqlalchemy import SQLAlchemy 
import mysql.connector 
app = Flask(__name__)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/db_library'
db_library = SQLAlchemy(app)

#conn = mysql.connector.connect(host='localhost', password='mysql', user='root', database='db_library')
#cursor = conn.cursor()
#insert_record = '''insert into db_library.library (username, email) values ('Munna', 'singh92munendra@gmail.com')'''
#cursor.execute(insert_record)
#conn.commit()
#conn.close()

class Library(db_library.Model):
    id = db_library.Column(db_library.Integer, primary_key=True)
    name = db_library.Column(db_library.String(100), nullable=False)
    address = db_library.Column(db_library.String(200), nullable=False)
    pricing = db_library.Column(db_library.String(500))
    total_number_of_seats = db_library.Column(db_library.Integer, default=0)  
    available_seats = db_library.Column(db_library.Integer, default=0)  
   # images = db_library.Column(db_library.Text)

    # Add CheckConstraints to ensure total number of seats and available seats are greater than or equal to 0
    __table_args__ = (
        db_library.CheckConstraint(total_number_of_seats > 0, name='positive_total_seats'),
        db_library.CheckConstraint(available_seats >= 0, name='positive_available_seats'),
    )

@app.route('/')
def index():
    return render_template('index.html')

# Define the create_library_profile route
@app.route('/create_library_profile')
def create_library_profile():
    return render_template('create_library.html')

# Define the user_login route
@app.route('/user_login')
def user_login():
    return render_template('user_login.html')


if __name__ == '__main__':
    app.run(debug=True)

