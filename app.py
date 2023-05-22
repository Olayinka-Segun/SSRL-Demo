from db.models import *
from flask import Flask,flash,render_template,session,request,redirect,url_for
#from flask_mysqldb import MySQL
from mysql.connector.connection import MySQLConnection
import MySQLdb.cursors
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sege_d_boy@2002'
app.config['MYSQL_DB'] = 'smartdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'loggedin' in session:
        flash('Welcome!')
        return render_template('home.html')
        
    else:
        return redirect(url_for('login')) 
    
@app.route('/login', methods = ["POST","GET"])
def login():
    flash('')
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        #Creating variables for easy access
        username = request.form['username']
        password = request.form['password']
        date_time = datetime.now()
        day = date_time.strftime("%A")

        app.logger.info(username)
        #check if the account exists using MySQL
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        mycursor.execute('SELECT * FROM interns WHERE username=%s AND password=%s',(username,password,))
        #Fetch one record and returns result
        interns = mycursor.fetchone()
        if interns:
            fullname = interns[1]
            id = interns[0]
            session['loggedin'] = True
            session['username'] = username
            session['id'] = id
            id = session['id']
            app.logger.info(id)
            #redirect to home page
            mycursor.execute(f"""UPDATE login SET {day} = %s WHERE fullname=%s""",(date_time, fullname,))
            db.commit() 
            flash('Logged in successfully!')  
            return render_template('home.html')
        else:
            flash('Invalid Username/Password!')
    return render_template('login.html')    
    
@app.route('/register', methods = ['POST','GET'])
def register():
    flash('')
    if request.method == 'POST' and 'fullname' in request.form and 'email' in request.form and 'phone' in request.form and 'username' in request.form and 'password' in request.form:
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        session['username'] = request.form['username']
        username = session['username']
        password = request.form['password']
        role = 'Admin'
        stack = request.form['stack']
        date_joined = datetime.now()

        email = request.form['email']    
        # checking if the account exists in the database
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        mycursor.execute('SELECT * FROM interns WHERE username=%s',(username,))
        interns = mycursor.fetchone()
        # if the account exist show an error 
        if interns:
            fullname = interns[1]
            session['fullname'] = fullname 
            flash('Account already exists!')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address!') 
        elif not re.match(r'[A-Za-z0-9]+',username): 
            flash('Username must contain only chatracters and number')
        elif not fullname or not email or not password or not username:
            flash('Please fill out the form!')
        else:
            mycursor.execute("INSERT INTO interns (fullname,email,phone,username,password,role,stack,date_joined) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(fullname,email,phone,username,password,role,stack,date_joined)) 
            db.commit() 
            mycursor.execute("INSERT INTO login (fullname,Monday,Tuesday,Wednesday,Thursday,Friday) VALUES(%s,%s,%s,%s,%s,%s)",(fullname,'','','','','',))
            db.commit()
            mycursor.execute("INSERT INTO logout (fullname,Monday,Tuesday,Wednesday,Thursday,Friday) VALUES(%s,%s,%s,%s,%s,%s)",(fullname,'','','','','',))
            db.commit()   
            mycursor.execute("INSERT INTO nature_of_work (fullname,Monday,Tuesday,Wednesday,Thursday,Friday) VALUES(%s,%s,%s,%s,%s,%s)",(fullname,'','','','','',))
            db.commit()   
            flash('You succesfully registered!') 
            return render_template('login.html')
            
    elif request.method == "POST":
        # the form is empty
        flash('Please fill out the form')
    return render_template('register.html')   

@app.route('/update',methods = ['POST','GET'])
def update():
    flash('')
    if 'loggedin' in session:
        if request.method == 'POST':
            fullname = request.form['fullname']
            email = request.form['email']
            phone = request.form['phone']
            username = request.form['username']
            stack = request.form['stack']
            #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            mycursor.execute('SELECT * FROM interns WHERE username=%s',(username,))
            interns = mycursor.fetchone()
            if interns:
                flash('Account already exists!')
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Invalid email address!') 
            elif not re.match(r'[A-Za-z0-9]+',username): 
                flash('Username must contain only chatracters and number')
            elif not fullname or not email or not username:
                flash('Please fill out the form!')
            else:
                mycursor.execute('UPDATE interns SET fullname=%s,email =%s, phone=%s,username=%s,stack=%s WHERE id=%s',(fullname,email,phone,username,stack,(session['id'],),))
                db.commit()
                flash('You have successfully updated !')
                return redirect (url_for('profile'))
        elif request.method == 'POST':
            flash('Please fill out the form')
        return render_template('update.html')  
    return redirect (url_for('login'))        

# Creating a function that delete the intern
@app.route('/interns/<int:user_id>', methods=['DELETE'])
def delete_intern(user_id):
    # Check if the user exists
    select_query = "SELECT * FROM users WHERE id = %s"
    mycursor.execute(select_query, (user_id,))
    user = mycursor.fetchone()

    if not user:
        return "User not found", 404

    # Delete the user profile from the database
    delete_query = "DELETE FROM users WHERE id = %s"
    mycursor.execute(delete_query, (user_id,))
    db.commit()

    return "User profile deleted successfully", 200

# Create the function runs the delete_interns
@app.route('/delete', methods=['DELETE'])
def delete():
    user_id = session['id']  # Replace with the appropriate user ID
    return redirect(url_for('delete_intern', user_id=str(user_id))) 

@app.route('/interns/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Retrieve user details from the database
    select_query = "SELECT * FROM interns WHERE id = %s"
    mycursor.execute(select_query, (user_id,))
    user = mycursor.fetchone()

    if user:
        # Prepare the response
        user_data = {
            'id': user[0],
            'fullname': user[1],
            'email': user[2],
            'phone' : user[3],
            'username': user[4],
            'role': user[6],
            'stack': user[7]
        }
        return render_template('profile.html', user=user_data)
    else:
        return "User not found"

@app.route('/profile', methods=['GET'])
def profile():
    user_id = session['id']  # Replace with the appropriate user ID
    return redirect(url_for('get_user', user_id=str(user_id)))   


@app.route('/interns')  
def interns():
    if 'loggedin' in session:
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('SELECT * FROM interns WHERE id=%s',(session['id'],))
        interns = mycursor.fetchall()
        return render_template('interns.html', interns=interns)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    flash("")
    fullname = session['fullname']
    if 'loggedin' in session:
        if request.method == "POST":
            date_time = datetime.now()
            day = date_time.strftime("%A")
            naw = request.form.get("naw")

            mycursor.execute(f"""UPDATE logout SET {day} = %s WHERE username=%s""",(date_time, fullname))
            db.commit()
            mycursor.execute(f"""UPDATE nature_of_work SET {day} = %s WHERE Username =%s""",(naw,fullname))
            db.commit()
            
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('username', None)
            flash('You have sucessfully logged out!')
            return redirect(url_for('index'))
        return render_template('logout.html')
    return redirect(url_for('index'))
 
 

if __name__ == "__main__":
    app.run(debug=True)