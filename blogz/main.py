from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'kjdshglbdhfjduoe'


class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title    
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username    
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('mainpage.html',users=users)


@app.route('/blog')
def blog():
   

    blog_id = request.args.get('id')
    user = request.args.get('user')
    if (blog_id):
        post = Blog.query.get(blog_id)
        return render_template('post.html', title="Blog Entry", post=post)
    elif (user):
        posts = Blog.query.filter_by(owner_id=user)
        return render_template('singleUser.html', posts=posts)
    posts = Blog.query.all()
    return render_template('blog.html',title="Amy's Blog Haven",
        posts=posts)


@app.route('/userposts')
def singleUser():

    active_user = session['username']
    active = User.query.filter_by(username = active_user ).first()
    posts = Blog.query.filter_by(owner_id = active.id).all()

    return render_template('singleUser.html', title="Your Blog Posts", posts=posts)




@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '' or body == '':
            flash('Title and Body cannt be blank' , 'error')
            return render_template('newpost.html', titleb=title, bodyb=body)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            post =  {
                    "title": title,
                    "body": body
                    }
            return render_template('post.html', post=post)
    else:
        return render_template('newpost.html', title="New Post")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        passwordA = request.form['passwordA']
        passwordB = request.form['passwordB']

       
        general_err = ""

        if username and passwordA and passwordB:
            if passwordA != passwordB:
                general_err = general_err + 'Password is incorrect. '
            if len(username) >= 3:
                user_exists = User.query.filter_by(username=username).first()
                if user_exists:
                    general_err = general_err + 'You already have an active account. Please login. '
            else: 
                general_err = general_err + 'Username cannot be less than 3 characters. '
            if len(passwordA) < 3:
                general_err = general_err + 'Password cannot be less than 3 characters. '     
        else:
            general_err = general_err + 'Password and/or username cannot be blank. '
        if not general_err:
           
            new_user = User(username, passwordA)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash(general_err , 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        active_user = User.query.filter_by(username=username).first()
        general_err = ''
        if active_user and password == active_user.password:
            flash('Logged In')
            session['username']=username
            return redirect('/newpost')
        else: 
            general_err = 'You do not have an active account. Please create One. '
            flash(general_err, 'error')
        return render_template('/login.html')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()