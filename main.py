from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzhw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abcdefghijklmnopqrstuvwxyz'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_blog = db.Column(db.String(120))
    body_blog = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title_blog, body_blog, owner):
        self.title_blog = title_blog
        self.body_blog = body_blog
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner' )

    def __init__(self, username, password):
        self.username = username
        self.password = password  

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'main_blog_page', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['GET', 'POST'])
def main_blog_page():
    blog_id = request.args.get('id')
    blogs = Blog.query.all()
  
    if blog_id:
        blog = Blog.query.get(blog_id)
        print(blog)
        return render_template('display_blog.html', blog=blog) 
    
    return render_template('blog.html', blogs=blogs)



@app.route('/add_to_homepage', methods=['GET','POST']) 
def add_to_homepage():
    new_title = request.form['title_blog']
    new_body = request.form['body_blog']
    
    if new_title == "" or new_body == "":
        error_title = "Please fill in the title"
        error_body = "Please fill in the body"
        return redirect("/newpost?error_title=" + error_title + '&error_body=' + error_body )
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        add_content = Blog(new_title, new_body, owner)
        db.session.add(add_content)
        db.session.commit()
    
        current_id = add_content.id
        return redirect('/blog?id={0}'.format(current_id))
             
                

@app.route('/newpost', methods=['GET','POST'])
def new_post():
    encoded_error = request.args.get("error_title")
    encoded_error1 = request.args.get("error_body")
    return render_template('/newpost.html', error_title=encoded_error, error_body=encoded_error1)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Password is incorrect')
        elif username != user:
            flash('Username does not exist')
            
    return render_template('login.html')         

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        
        if username == "" or password == "" or verify == "":
            flash('One or more fields are invalid') 
            return render_template('signup.html')
        if len(username) < 3:
            flash('Invalid username')
            return render_template('signup.html')
        if len(password) < 3:
            flash('Invalid password') 
            return render_template('signup.html')

        if not existing_user and password == verify:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
         
        if password != verify:
            flash('Passwords do not match') 
        if existing_user:
            flash('User already exists') 
              
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
@app.route('/index')
def index():
    owners = User.query.all()
    print(owners)
    return render_template('index.html', owners=owners) 

@app.route('/user')
def user_blog():
    blogs = Blog.query.all()
    user = User.query.all()
    user_id = request.args.get('id')
    print(user_id)

    if user_id:
        
        user = User.query.filter_by(id=user_id).all()
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        
    return render_template('user.html',user=user,blogs=blogs)
     

if __name__ == '__main__':
    app.run()