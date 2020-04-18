import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm1,PostForm2
from flaskblog.models import User, Post, Notification
from flask_login import login_user, current_user, logout_user, login_required
import random

@app.route("/")
@app.route("/home")
def home():
    page=request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=100)
    return render_template('home.html', posts=posts)

@app.route("/home2")
def home2():
    if current_user.decline_flag==True:
        if current_user.usertype=="Consumer":
            flash('Your recent Request for Food has been Rejected. Check Notifications', 'success')
        else :
            flash('Your recent Offer for Providing Food has been Rejected. Check Notifications', 'success')
    current_user.decline_flag = False
    db.session.commit()
    if current_user.accept_flag==True:
        if current_user.usertype=="Consumer":
            flash('Your recent Request for Food has been Accepted. Check Notifications', 'success')
        else :
            flash('Your recent Offer for Providing Food has been Accepted. Check Notifications & Secret Key for Number Lock !!', 'success')
    current_user.accept_flag = False
    db.session.commit()
    page=request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=100)
    return render_template('home2.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home2'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,usertype=form.usertype.data,location=form.location.data,email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home2'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home2'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    current_user.key_flag=False
    notifications = Notification.query.order_by(Notification.date_posted.desc())
    for notification in notifications:
      if notification.owner==current_user:
        notification.new_flag=False   
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.location.data = current_user.location
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form1 = PostForm1()
    form2 = PostForm2()

    if form1.validate_on_submit():
        post = Post(food=form1.food.data,people=form1.people.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home2'))

    if form2.validate_on_submit():
        post = Post(food=form2.food.data,people=form2.people.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home2'))
    return render_template('create_post.html', title='New Post',
                           form1=form1,form2=form2, legend='New Post')

@app.route("/confirmmatch/<int:post_id>/<int:current_id>")
def confirmmatch(post_id,current_id):
    print("Executing confirmmatch")
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(current_id)
    post.matchrequest=False
    post.requestpartner= "00"
    post.requestpartnerid= -1
    if user.RequestOUT_flag != 0:
        user.RequestOUT_flag-=1
    user.RequestCheythaAldeID=-1
    if post.author.RequestIN_flag != 0:
        post.author.RequestIN_flag-=1
    db.session.commit()
    return render_template('confirmmatch.html', post=post)

@app.route("/confirmmatch2/<int:post_id>/<int:current_id>")
def confirmmatch2(post_id,current_id):
    print("Executing confirmmatch2")
    post = Post.query.get_or_404(post_id)
    userA = User.query.get_or_404(current_id)
    userB = User.query.get_or_404(post.author.id)
    post.matchrequest=True
    post.requestpartner=userA.username
    post.requestpartnerid=userA.id
    userA.RequestOUT_flag+=1
    userA.RequestCheythaAldeID=userB.id
    userB.RequestThannaAldeID=userA.id
    userB.RequestIN_flag+=1
    db.session.commit()
    return render_template('confirmmatch2.html', post=post)

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form1 = PostForm1()
    form2 = PostForm2()
    if form1.validate_on_submit():
        post.food = form1.food.data
        post.people = form1.people.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home2', post_id=post.id))
    if form2.validate_on_submit():
        post.food = form2.food.data
        post.people = form2.people.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home2', post_id=post.id))
    elif request.method == 'GET':
        form1.food.data = post.food
        form1.people.data = post.people
        form2.food.data = post.food
        form2.people.data =post.people
    return render_template('create_post.html', title='Update Post',
                           form1=form1,form2=form2, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home2'))

@app.route("/requests")
@login_required
def requests():
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=100)
    page=request.args.get('page',1,type=int)
    notifications = Notification.query.order_by(Notification.date_posted.desc()).paginate(per_page=300)
    return render_template('requests.html',posts=posts,notifications=notifications)

@app.route("/requests/<int:post_id>/<int:partner_id>/decline")
def decline_requests(post_id,partner_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(partner_id)
    post.findrequest_flag=False
    post.matchrequest=False
    post.requestpartner= "00"
    post.requestpartnerid= -1
    user.RequestOUT_flag-=1
    user.decline_flag = True
    current_user.RequestIN_flag-=1
    notification = Notification(PartnerName=post.author.username,PartnerId=post.author.id,status="Rejected", owner=user)
    db.session.add(notification)
    db.session.commit()
    flash('Match request has been rejected!', 'success')
    return redirect(url_for('requests'))

@app.route("/requests/<int:post_id>/<int:partner_id>/confirm")
@login_required
def confirm_requests(post_id,partner_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(partner_id)
    if post.author != current_user:
        abort(403)
    user.RequestOUT_flag-=1
    current_user.RequestIN_flag-=1
    user.accept_flag = True
    user.donation += post.people
    notification = Notification(PartnerName=post.author.username,PartnerId=post.author.id,status="Accepted", owner=user)
    db.session.add(notification)
    post.author.donation += post.people  
    db.session.delete(post)
    db.session.commit()
    flash('Your food has been Matched successfully and Post has been deleted from Home!', 'success')
    return redirect(url_for('requests'))

@app.route("/profile/<int:profile_id>")
def profile(profile_id):
    user = User.query.get_or_404(profile_id)
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('profile.html', title='Profile',image_file=image_file, user=user)

@app.route("/history")
def history():
    page=request.args.get('page',1,type=int)
    notifications = Notification.query.order_by(Notification.date_posted.desc()).paginate(per_page=10)
    return render_template('history.html', notifications=notifications)
   
@app.route("/find/<int:post_idyo>/<string:post_food>/<int:post_people>")
def find(post_idyo, post_food, post_people):
    print("Executing find")
    page=request.args.get('page',1,type=int)
    post= Post.query.get_or_404(post_idyo)
    posts1 = Post.query.order_by(Post.people.desc()).paginate(per_page=100)
    posts2 = Post.query.order_by(Post.people.asc()).paginate(per_page=100)
    return render_template('find.html', posts1=posts1, posts2=posts2, post_idyo=post_idyo, post_food=post_food, post_people=post_people)

@app.route("/generatekey/<int:not_id>/<int:partner_id>")
def generatekey(not_id,partner_id):
    key=random.randint(1101,9999)
    notification= Notification.query.get_or_404(not_id)
    notification.generatekey_flag=False
    user= User.query.get_or_404(partner_id)
    user.key=key
    user.key_flag=True
    user.KeyThannaAal=current_user.username
    db.session.commit()
    return render_template('generatekey.html',key=key,notification=notification)


@app.route("/confirmfindmatch/<int:post_id>/<int:current_id>/<int:findpost_id>")
def confirmfindmatch(post_id,current_id,findpost_id):
    print("Executing confirmfindmatch")
    post = Post.query.get_or_404(post_id)  
    user = User.query.get_or_404(current_id)
    post.findrequest_flag=False
    post.findrequestpostid=-1
    post.matchrequest=False
    post.requestpartner= "00"
    post.requestpartnerid= -1
    if user.RequestOUT_flag != 0:
        user.RequestOUT_flag-=1
    user.RequestCheythaAldeID=-1
    if post.author.RequestIN_flag != 0:
        post.author.RequestIN_flag-=1
    db.session.commit()
    return render_template('confirmfindmatch.html', post=post, findpost_id=findpost_id)

@app.route("/confirmfindmatch2/<int:post_id>/<int:current_id>/<int:findpost_id>")
def confirmfindmatch2(post_id,current_id,findpost_id):
    print("Executing confirmfindmatch2")
    post = Post.query.get_or_404(post_id)
    post.findrequest_flag=True
    post.findrequestpostid=findpost_id
    userA = User.query.get_or_404(current_id)
    userB = User.query.get_or_404(post.author.id)  
    post.matchrequest=True
    post.requestpartner=userA.username
    post.requestpartnerid=userA.id
    userA.RequestOUT_flag+=1
    userA.RequestCheythaAldeID=userB.id
    userB.RequestThannaAldeID=userA.id
    userB.RequestIN_flag+=1
    db.session.commit()
    return render_template('confirmfindmatch2.html', post=post,findpost_id=findpost_id)



@app.route("/findrequests/<int:post_id>/<int:partner_id>/<int:findpost_id>/confirm")
@login_required
def confirm_findrequests(post_id,partner_id,findpost_id):
    post = Post.query.get_or_404(post_id)
    findpost=Post.query.get_or_404(findpost_id)
    user = User.query.get_or_404(partner_id)
    if post.author != current_user:
        abort(403)
    user.RequestOUT_flag-=1
    current_user.RequestIN_flag-=1
    user.accept_flag = True
    notification = Notification(PartnerName=post.author.username,PartnerId=post.author.id,status="Accepted", owner=user)
    db.session.add(notification)
    db.session.delete(post)
    db.session.delete(findpost)
    db.session.commit()
    flash('Your food has been Matched successfully and Post has been deleted from Home!', 'success')
    return redirect(url_for('requests'))

@app.route("/ranking")
def ranking():
    page=request.args.get('page',1,type=int)
    users = User.query.order_by(User.donation.desc()).paginate(per_page=100)
    return render_template('ranking.html', users=users)