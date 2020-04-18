from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    usertype = db.Column(db.String(20),nullable=False)
    location = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    donation = db.Column(db.Integer,default=0)
    accept_flag = db.Column(db.Boolean,default=False)
    decline_flag = db.Column(db.Boolean,default=False)
    RequestIN_flag = db.Column(db.Integer,default=0)
    RequestOUT_flag = db.Column(db.Integer,default=0)
    RequestCheythaAldeID = db.Column(db.Integer,default=-1)
    RequestThannaAldeID= db.Column(db.Integer,default=-1)
    key=db.Column(db.Integer)
    key_flag=db.Column(db.Boolean,default=False)
    KeyThannaAal= db.Column(db.String(20))
    posts = db.relationship('Post', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    food = db.Column(db.String(30),default="No Specification")
    people = db.Column(db.Integer,default=0)
    matchrequest = db.Column(db.Boolean, default=False)
    requestpartner = db.Column(db.String(20),default="000")
    requestpartnerid = db.Column(db.Integer,default=-1)
    findrequest_flag = db.Column(db.Boolean, default=False)
    findrequestpostid = db.Column(db.Integer,default=-1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.food}', '{self.date_posted}')"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    PartnerName=db.Column(db.String(25),nullable=False)
    status=db.Column(db.String(10),nullable=False)
    new_flag=db.Column(db.Boolean,default=True)
    generatekey_flag=db.Column(db.Boolean,default=True)
    PartnerId=db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Notification('{self.PartnerName}', '{self.status}','{self.new_flag}')"