from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thisismysupersecretkey'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(280))
    owner_id = db.Column(db.Integer)
#    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_entry):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner_id = 1
        
#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(120), unique=True)
#    password = db.Column(db.String(120))
#    tasks = db.relationship('Task', backref='owner')
#
#    def __init__(self, email, password):
#        self.email = email
#        self.password = password

#@app.before_request
#def require_login():
#    allowed_routes = ['login', 'register']
#    if request.endpoint not in allowed_routes and 'email' not in session:
#        return redirect('/login')

#@app.route('/login', methods=['POST','GET'])
#def login():
#    if request.method == 'POST':
#        email = request.form['email']
#        password = request.form['password']
#        user = User.query.filter_by(email=email).first()
#        if user and user.password == password:
#            session['email'] = email
#            flash('Logged in')
#            return redirect('/')
#        else:
#            flash('User password incorrect or user not registered', 'error')
#
#   return render_template('login.html')

#@app.route('/register', methods=['POST','GET'])
#def register():
#    if request.method == 'POST':
#        email = request.form['email']
#        password = request.form['password']
#        verify = request.form['verify']
#
#        #TODO - validate information
#
#        existing_user = User.query.filter_by(email=email).first()
#        if not existing_user:
#            new_user = User(email, password)
#            db.session.add(new_user)
#            db.session.commit()
#            session['email'] = email
#            return redirect('/')
#        else:
#            # TODO Error existing user message
#            return '<h1>Duplicate User</h1>'
#
#    return render_template('register.html')

#@app.route('/logout')
#def logout():
#    del session['email']
#    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_entry = request.form['blog_entry']
        owner = 1
        #TODO verify title and entry not blank if so redirect and flash
#        new_entry = Blog(blog_title, blog_entry, owner)
        if blog_title == '' and blog_entry == '':
            flash('You must enter both a title and an entry.', 'error')
            return redirect('/newpost')
        elif blog_title == '':
            flash('You must enter a title.', 'error')
            return redirect('/newpost')
        elif blog_entry == 'Write new entry here...':
            flash('You must include an entry.', 'error')
            return redirect('/newpost')

        new_entry = Blog(blog_title, blog_entry)
        db.session.add(new_entry)
        db.session.commit()

        return redirect('/')
    return render_template('newpost.html', title='New Post')


@app.route('/')
def index():

    blogs = Blog.query.all()

    return render_template('blogs.html', title="Blogs", blogs=blogs)


if __name__ == '__main__':
    app.run()