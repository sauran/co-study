from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import MySQLdb
app = Flask(__name__)
app.static_url_path = '/static'
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images') # Folder to store uploaded images


@app.route('/', methods=['GET', 'POST'])  # Add 'GET' and 'POST' methods here
def index():
    unique_cities = get_unique_cities()
    if request.method == 'POST':
        selected_city = request.form.get('selected_city')
        libraries = search_libraries_by_city(selected_city)
        return render_template('index.html', libraries=libraries, selected_city=selected_city,unique_cities=unique_cities)
    
    return render_template('index.html', unique_cities=unique_cities)

@app.route('/search_results', methods=['POST'])
def search_results():
    unique_cities = get_unique_cities()
    if request.method == 'POST':
        selected_city = request.form.get('selected_city')
        libraries = search_libraries_by_city(selected_city)
        return render_template('lib_search_result_list.html', libraries=libraries, selected_city=selected_city,unique_cities=unique_cities)
    
    return render_template('lib_search_results_list.html', unique_cities=unique_cities)

def get_unique_cities():
    connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT lib_city FROM library_details")
    unique_cities = cursor.fetchall()
    connection.close()
    return unique_cities

def get_library_details(lib_id):
    conn = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    query = "SELECT * FROM library_details WHERE lib_id = %s"
    cursor.execute(query, (lib_id,))
    library = cursor.fetchone()
    
    conn.close()
    return library

def search_libraries_by_city(city):
    connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM library_details WHERE lib_city = %s", (city,))
    libraries = cursor.fetchall()
    connection.close()
    return libraries


# Function to search for libraries based on pincode
def search_libraries(pincode):
    conn = MySQLdb.connect(host='localhost', user='sauran', passwd='mysql', db='db_library')
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM library WHERE lib_pincode = %s"
    cursor.execute(query, (pincode,))
    libraries = cursor.fetchall()
    conn.close()
    return libraries

# Function to get libraries added by a specific owner
def get_libraries_by_owner(owner_username):
    conn = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM library WHERE owner_username = %s"
    cursor.execute(query, (owner_username,))
    libraries = cursor.fetchall()
    conn.close()
    return libraries


@app.route('/library_details/<int:lib_id>')
def library_details(lib_id):
    library = get_library_details(lib_id)  # Implement this function to fetch library details by lib_id
    return render_template('library_details_page.html', library=library)



# Define the owner signup route
@app.route('/owner_signup', methods=['GET', 'POST'])
def owner_signup():
    if request.method == 'POST':
        owner_fullname = request.form['owner_fullname']
        owner_mobileno = request.form['owner_mobileno']
        owner_emailid = request.form['owner_emailid']
        owner_username = request.form['owner_username']
        owner_password = request.form['owner_password']

        connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO owners (owner_fullname, owner_mobileno, owner_emailid, owner_username, owner_password) VALUES (%s, %s, %s, %s, %s)",
                       (owner_fullname, owner_mobileno, owner_emailid, owner_username, owner_password))
        connection.commit()
        connection.close()


        # You can redirect to the login page after successful signup
        return redirect(url_for('owner_login'))

    return render_template('owner_signup.html') 

# Define the owner login route
@app.route('/owner_login', methods=['GET', 'POST'])
def owner_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM owners WHERE owner_username = %s AND owner_password = %s",
                       (username, password))
        owner = cursor.fetchone()
        connection.close()

        if owner:
            # Fetch libraries added by the owner
            libraries = get_libraries_by_owner(owner['owner_username'])

            return render_template('owner_profile.html', owner=owner, libraries=libraries)
        else:
            error_message = "Invalid username or password."
            return render_template('owner_login.html', error_message=error_message)

    return render_template('owner_login.html')


# Define the route to add library details
@app.route('/add_library', methods=['GET', 'POST'])
def add_library():
    if request.method == 'POST':
        lib_name = request.form['lib_name']
        lib_address = request.form['lib_address']
        lib_city = request.form['lib_city']
        lib_pincode = request.form['lib_pincode']
        lib_timings = request.form['lib_timings']
        lib_pricing = request.form['lib_pricing']
        lib_amenties = request.form['lib_amenties']
        uploaded_files = request.files.getlist('lib_images[]')
        image_paths = ""

        for i, lib_images in enumerate(uploaded_files):
            if lib_images.filename != '':
                filename = secure_filename(lib_images.filename)
                # print("the filename is", filename)
                lib_folder = os.path.join(app.config['UPLOAD_FOLDER'], lib_name)
                Path(lib_folder).mkdir(parents=True, exist_ok=True)
                filepath = os.path.join(lib_folder, filename)
                #filepath = os.path.join("images", lib_name, filename)
                #print (filepath)
                #print(lib_folder)
                lib_images.save(filepath)
                if i == 0:
                    image_paths += '/images/'+lib_name+'/'+filename
                else:
                    image_paths += ';/images/'+lib_name+'/'+filename
                #image_paths.append('/images/'+lib_name+'/'+filename)
        lib_ownercontactinfo = request.form['lib_ownercontactinfo']

        # Insert the library details into the database
        connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_library')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO library_details (lib_name,lib_address,lib_city, lib_pincode,lib_timings, lib_pricing,lib_amenties,lib_images,lib_ownercontactinfo) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)",
                       (lib_name, lib_address,lib_city,lib_pincode, lib_timings, lib_pricing,lib_amenties,image_paths,lib_ownercontactinfo))
        connection.commit()
        connection.close()

        return render_template('added_succesfully.html')
    
    
    return render_template('add_library_details.html')  # Display the library details form

# Define the user_login route
""" @app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_student')
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM students WHERE student_mobile = %s AND student_password = %s",
                       (mobile, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            # User is authenticated, you can proceed to a logged-in page
            return render_template('user_profile.html', user=user)
        else:
            # User authentication failed, show an error message
            print ('test print')
            error_message = "Invalid mobile number or password."
            return render_template('user_login.html', error_message=error_message)

    return render_template('user_login.html') """




""" @app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']

        connection = MySQLdb.connect(host='localhost', user='root', password='mysql', db='db_student')
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        result = cursor.execute("INSERT INTO students (student_name, student_mobile, student_email, student_password) VALUES (%s, %s, %s, %s)",
                       (name, mobile, email, password))
        

        connection.commit()
        connection.close()

        # You can redirect to the login page after successful signup
        return redirect(url_for('user_login'))

    return render_template('user_signup.html') """

# Define the user profile route
""" @app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']

        connection = MySQLdb.connect(host='localhost', user='sauran', password='mysql', db='db_student')
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM students WHERE student_mobile = %s AND student_password = %s",
                       (mobile, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            return render_template('user_profile.html', user=user)
        else:
            error_message = "Invalid mobile number or password."
            return render_template('user_login.html', error_message=error_message)

    return render_template('user_profile.html')  # Display the user profile page """


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

