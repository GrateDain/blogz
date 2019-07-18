from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thisismysupersecretkey'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(280))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry, id):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner_id = id
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    name =db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register','all_blogz', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_email = User.query.filter_by(email=email).first()
        if user_email and user_email.password == password:
            session['email'] = email
            session['name'] = user_email.name
            session['id'] = user_email.id
            flash(session['name'] + ' logged in', 'info')
            return redirect('/newpost')
        elif not user_email:
            flash('User email incorrect or not registered', 'error')
        elif user_email.password != password:
            flash('User password incorrect.', 'error')

    return render_template('login.html', title='Log In')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

#        TODO - validate information
        if len(username) < 3 or len(password) < 3:
            flash('User name and password must be at least 3 characters.', 'error')
            return redirect('/register')
        if username == '' or password == '' or email == '':
            flash('You must enter a user name, password and email', 'error')
            return redirect('/register')

        existing_user = User.query.filter_by(name=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('User name is already taken.', 'error')
            return redirect('/register')
        elif existing_email:
            flash('Email is already signed up.', 'error')
            return redirect('/login')
        else:
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            session['name'] = username
            flash(session['name'] + ' logged in', 'info')
            return redirect('/newpost')

    return render_template('register.html', title='Sign Up')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_entry = request.form['blog_entry']
        owner = User.query.filter_by(name=session['name']).first()

        if blog_title == '' and blog_entry == '':
            flash('You must enter both a title and an entry.', 'error')
            return redirect('/newpost')
        elif blog_title == '':
            flash('You must enter a title.', 'error')
            return redirect('/newpost')
        elif blog_entry == 'Write new entry here...':
            flash('You must include an entry.', 'error')
            return redirect('/newpost')

        new_entry = Blog(blog_title, blog_entry, owner.id)
        db.session.add(new_entry)
        db.session.commit()

        newblog = Blog.query.order_by(Blog.id.desc()).first()
        newblog_id = newblog.id
        owner = User.query.filter_by(id=newblog.owner_id).first()   

        return render_template('/single_blog.html', title='Your new post', singleblog=newblog, author=owner.name)
    return render_template('newpost.html', title='New Post')

@app.route('/singleauthor')
def single_author():
    author = request.args.get('author')
    owner = User.query.filter_by(name=author).first()
    blogs = Blog.query.filter_by(owner_id=owner.id).all()
    return render_template('single_author.html', title='Posts by '+ author, blogs=blogs, author=author)

@app.route('/singleblog')
def single_blog():
    blog_id = request.args.get('blogid')
    singleblog = Blog.query.filter_by(id=blog_id).first()
    owner = User.query.filter_by(id=singleblog.owner_id).first()
    return render_template('single_blog.html', title=singleblog.blog_title, singleblog=singleblog, author=owner.name)

@app.route('/allposts')
def all_blogz():
    allblogs= Blog.query.all()
    authors = User.query.all()
    return render_template('all_blogs.html', title='All Blogz Posts', blogs=allblogs, author=authors)

@app.route('/')
def index():
    authors = User.query.all()
    return render_template('index.html', title="Blogs", authors=authors)

@app.route('/test')
def test():
    return '<p>' + str(session['id']) + '</p>'

if __name__ == '__main__':
    app.run()