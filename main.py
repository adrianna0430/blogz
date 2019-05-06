from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:NewPass@localhost:8889/blogz'
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'JlJKL9876KJiY8uy8ygysdo(US&Alkw;w'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#USER ONLY ROUTES
@app.before_request
def require_login():
    # requires user be logged in before being allowed to create a new blog post
    allowed_routes = ['login', 'list_blogs', 'index', 'signup', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#SIGNUP PAGE
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template('signup.html')

    username = request.form["username"]
    password = request.form["password"]
    verify = request.form["verify"]
    user = User.query.filter_by(username=username).first()

    # Verify Username
    if username == "":
        username_error = "Username cannot be blank"
    elif len(username) < 3 or len(username)>20:
        username_error = "Name must be between 3 and 20 characters."
    elif user: 
        username_error = "That username already exists.  Please make a different username."
    else:
        username_error = ""

    # Verify Password
    if password == "" and not user: 
        password_error = "Password field cannot be blank"
    elif (len(password) < 3 or len(password) > 20) and not user: 
        password_error = "Password must be between 3 and 20 characters long"
    else:
        password_error = ""

    # Verify Password is Verified
    if verify == "" and not user: 
        verify_error = "Please verify your password"
    elif verify != password and not user: 
        verify_error = "Passwords do not match"
    else:
        verify_error = ""

    # Add new user to the database, create a new session, and send to make a new post
    if not username_error and not password_error and not verify_error:
        if request.method == "POST":
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        # Renders signup with error messages 
        return render_template('signup.html', username = username, username_error = username_error, 
            password_error = password_error, verify_error = verify_error)
    
#LOGIN
@app.route('/login', methods=["POST", "GET"])
def login(): 
    if request.method == "GET":
        return render_template('login.html')

    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    # Verify Username
    if username == "":
        username_error = "Enter your username"
    elif not user: 
        username_error = "User not found"
    else:        
        username_error = ""

    # Verify Password
    if password == "" and user: 
        password_error = "Enter your password" 
    elif user: 
        if user.password!=password:
            password_error = "Incorrect Password"
        else:
            password_error = ""
    elif not user: 
        password_error = ""
    
    # Login, create new session and redirect to create a new post
    if username_error == "" and  password_error == "":
        if request.method == 'POST':
            if user and user.password==password:
                session['username'] = username
                flash("logged in")
                return redirect('/newpost') 

    # re-renders login template with appropriate error messages if login errors exist
    else:
        return render_template('login.html', username = username, 
            username_error = username_error, password_error = password_error)


#HOME PAGE W/ ALL USERS
@app.route('/', methods=["POST", "GET"])
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

#LOGOUT   
@app.route('/logout')
def logout():
    if session:
        del session['username']
        flash("logged out")
    return redirect('/blog')


#DISPLAY BLOG POSTS
@app.route('/blog', methods=["POST", "GET"])
def list_blogs():
    posts = Blog.query.all()
    
    # Individual Post
    if "id" in request.args:
        id = request.args.get('id')
        entry = Blog.query.get(id)
        
        return render_template('blog.html', title = entry.title, body = entry.body, owner = entry.owner)

    # All posts by a user
    if "user" in request.args:
        owner_id = request.args.get('user')
        userPosts = Blog.query.filter_by(owner_id=owner_id)
        username = User.query.get(owner_id)

        return render_template('singleUser.html', userPosts = userPosts, user = username)

    # All blog posts on site
    return render_template('all_blogs.html', posts = posts)

#CREATE A NEW POST
@app.route('/newpost', methods=["POST", "GET"])
def add_entry():
    if request.method == "GET":
        return render_template('new_blog.html')

    title = request.form["title"]
    body = request.form["body"]

    #Verify the title field
    if title == "":
        title_error = "Blog entry must have a title."
    else:
        title_error = "" 

    #Verify the body field
    if body == "":
        body_error = "Blog entry must have content."
    elif len(body) > 1000:
        body_error = "Blog entry cannot be more than 1000 characters long."
    else:
        body_error = ""
    
    #Add new entry to the database and redirect posts
    if not title_error and not body_error:
        if request.method == "POST":
            owner = User.query.filter_by(username =session['username']).first()
            new_entry = Blog(title, body, owner) 
            db.session.add(new_entry)
            db.session.commit()
        
        return render_template('blog.html', title = title, body = body, owner = owner)
    else:
        return render_template('new_blog.html', title = title, 
            title_error = title_error, body = body, body_error = body_error)

if __name__ == '__main__':
    app.run()






















