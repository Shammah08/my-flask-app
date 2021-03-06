from flask import Flask, render_template, request, redirect, abort, url_for, session, flash
from models import *
import hashlib

app = Flask(__name__)
# FOR SESSIONS
app.secret_key = 'MyVerySecretKey'


# TEMPLATE ROUTES
# LOGIN PAGE


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# USER AUTH AND LOG IN


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        session.pop('userid', None)
        session.pop('username', None)
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        response = log_in(username=username, password=password)
        if response == 'Wrong password!!':
            return render_template('login.html', response=response)
        elif response == 'Username not found!!':
            return render_template('login.html', response=response)
        else:
            # SUCCESSFUL LOGIN
            session['username'] = username
            session['userid'] = profile_data(username)[0][0]
            data = profile_data(username)
            return redirect(url_for('profile'))


@app.route('/logout')
def log_out():
    title = 'Logout'
    try:
        username = session['username']
        session.pop('username', None)
        session.pop('userid', None)
        return redirect('login')
    except KeyError:
        return render_template('error.html', title=title)


# VISIT OWN PROFILE- PERSONAL

@app.route('/profile')
def profile():
    title = "My Profile"
    try:
        userid = session['userid']
        username = session['username']
        data_profile = profile_data(username)
        data = user_profile(userid)
        posts = get_all_posts(userid)
        count = len(posts[1])
        mycount = len(posts[0])
        return render_template('profile.html', profile=data_profile, username=username, count=count, title=title, data=data, posts=posts,
                               mycount=mycount)
    except KeyError:
        return render_template('error.html', title=title)
    


# TO-DO LIST PAGE


@app.route('/my-to-do', methods=['GET', 'POST'])
def my_to_do():
    username = session['username']
    userid = session['userid']
    title = 'My To-Do'
    if request.method == 'GET':
        todo = get_to_do(userid)
        return render_template('todo.html', title=title, todo=todo, username=username)

    else:
        task = request.form['task']
        status = request.form['status']
        add_to_do(userid,  task, status)
        return redirect(url_for('my_to_do'))


# CREATE NEW TO-DO


@app.route('/create/to-do', methods=['POST', 'GET'])
def to_do_create(username, userid):
    userid = session['userid']
    username = session['username']
    task = request.form['task']
    status = request.form['status']
    add_to_do(userid,task, status)
    return redirect(url_for('my-to-do'))


@app.route('/task/<int:taskid>/delete')
def delete_task(taskid: int):
    username = session['username']
    userid = session['userid']
    task_delete(taskid,username,userid)
    return redirect(url_for('my_to_do'))

@app.route('/task/<int:taskid>/edit')
def edit_task(taskid: int):
    return  edit_to_do(taskid,username,task,status)

# VISIT ANY USERS PROFILE AS GUEST


@app.route('/profile/guest-<guest_username>')
def guest_profile(guest_username):
    try:
        username = session['username']
        # get guest userid
        userid = session['userid']
        # Check the user requesting the profile and the user profile being requested

        if username != guest_username:
            profile = profile_data(guest_username)
            data = get_all_posts(profile[0][0])
            count = len(data[1])
            mycount = len(data[2])
            title = f"{guest_username}'s profile"
            return render_template('profile.html', profile=profile, username=username, count=count, mycount=mycount,
                                   title=title, data=data, guest_username=guest_username)
        else:
            # WHEN YOU VISIT YOUR PROFILE

            return redirect(url_for('profile'))
    except KeyError:
        title = username
        return render_template('error.html', title=title)


# ADMIN PAGE


@app.route('/adminpanel')
def admin_panel():
    title = 'Administration'
    userid = session['userid']
    username= session['username']
    try:
        # check session name
        status = f"You are logged in as {session['username']}"
        if session['username'] == 'Admin':
            data = admin(username, userid)
            return render_template('adminpanel.html', data=data)

        else:
            # standard user error
            return abort(401)
    except KeyError:
        return render_template('error.html', title=title)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    title = 'Signup'
    if request.method == 'GET':
        return render_template('signup.html', title=title)
    else:
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        code = hashlib.sha256(f'{str(password)}'.encode()).hexdigest()
        sign_up(fname, lname, email, username, code)
        session['username'] = username
        session['userid'] = profile_data(username)[0][0]
        return redirect(url_for('setting'))


@app.route('/settings', methods=['POST', 'GET'])
def setting():
    username = session['username']
    userid = session['userid']
    if request.method == 'GET':
        data = profile_data(username)
        return render_template('settings.html', data=data, username=username)
    else:
        first_name = request.form['fname']
        last_name = request.form['lname']
        email = request.form['email']
        uname = request.form['username']
        about = request.form['about']
        edit_profile(userid,first_name,last_name,email,uname,about)
        data = profile_data(uname)
        status = 'Update Successful!!'
        return render_template('settings.html', data=data, status=status, username=username)


@app.route('/blog')
def blog():
    title = 'Blog'
    try:
        userid = session['userid']
        username = session ['username']
        post = get_all_posts(userid)
        count = len(post[1])
        return render_template('blog.html', post=post, count=count, username=username, title=title)
    except KeyError:
        return render_template('error.html', title=title)


# CREATE COMMENT
@app.route('/comment/<int:post_id>', methods=['POST'])
def comments(post_id):
    userid = session['userid']
    username = session['username']
    content = request.form['comment']
    comment(userid,username,post_id, content)
    return  post(post_id)

# DELETE COMMENT
@app.route('/comment/<int:post_id>/<int:comment_id>/<comment>')
def del_comments(post_id: int,comment_id: int, comment: str) ->None:
    userid = session['userid']
    username = session['username']
    del_comment(userid,username,comment_id,comment, post_id)
    return  post(post_id)


# CREATE NEW POST 
@app.route('/blog/create', methods=['GET', 'POST'])
def create():
    title = 'New Post'
    username = session['username']
    userid = session['userid']
    if request.method == 'GET':
        return render_template('newposts.html', title=title, username=username)
    else:
        author = username
        title = request.form['title']
        content = request.form['content']
        if request.form.getlist('yes'):
            privacy = 'Yes'
        else:
            privacy = "No"
        create_post(author, title, content, privacy,userid)
        if privacy == 'Yes':
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('blog'))


#ALL MY POSTS


@app.route('/<username>/myposts')
def myposts(username):
    if username == session['username']:
        userid = session['userid']
        posts = get_all_posts(userid)[0]
        comments = [len(get_all_posts(userid)[4]),get_all_posts(userid)[4]]
        count = len(posts)
        return render_template('myposts.html', posts=posts, count=count, comments=comments,username=username,profile_username=username)
    else:
        active_username = session['username']
        user = profile_data(username)
        userid = user[0][0]
        profile_username = user[0][4]
        posts = get_all_posts(userid)[2]
        comments = [len(get_all_posts(userid)[4]),get_all_posts(userid)[4]]
        return render_template('myposts.html', posts=posts, username=active_username,comments=comments,profile_username=profile_username)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/clear', methods=['GET'])
def clear():
    return render_template('update.html')


@app.route('/play')
def play():
    title = 'Play'
    return render_template('play.html', title=title)


# ACTIONS
# SEARCH APP


@app.route('/search/<keyword>', methods=['POST'])
def search(keyword):
    userid = session['userid']
    username = session['username']
    keyword = request.form['keyword']
    title = f'Results for {keyword}'
    result = db_search(userid, username, keyword)
    users = [len(result[0]), result[0]]
    posts = (len(result[1]), result[1])
    titles = (len(result[2]), result[2])
    comments = (len(result[3]), result[3])
    return render_template('result.html', users=users, posts=posts, titles=titles, comments=comments, keyword=keyword, title=title, username=username)


# GET POST


@app.route('/blog/<int:id>')
def post(id):
    username = session['username']
    userid = session['userid']
    data = get_all_posts(userid)
    users = user_profile(userid)
    count = len(data[1])
    content = get_post(id)
    comments = get_comment(id)
    return render_template('post.html', content=content, count=count,users=users, username=username, userid=userid, comments=comments )


# BLOG NAVIGATION
# FIX TO NAVIGATE THROUGH PUBLIC POSTS ONLY


@app.route('/blog/next/<int:id>')
def next(id):
    username = session['username']
    userid = session['userid']
    public_posts = get_all_posts(userid)[1]
    # private_id = private_post(userid)[0]
    personal_posts = get_all_posts(userid)[0]
    private_id = []
    public_id = []
    for item in personal_posts:
        private_id.append(item[0])
    for item in public_posts:
        public_id.append(item[0])
    try:
        if id in public_id:
            position = public_id.index(id)
            nxt = position - 1
            return post(public_id[nxt])
        else:
            if id in private_id:
                position = private_id.index(id)
                nxt = position - 1
                return post(private_id[nxt])       
    except  Exception as error:
        return f'<h2>An error  has occured </h2><br>{error} <br><h4>Contact Support For Assistance</h4> <br> <a href="/blog/{id}">Home</a>'

@app.route('/blog/previous/<int:id>')
def previous(id):
    username = session['username']
    userid = session['userid']
    public_posts = get_all_posts(userid)[1]
    # private_id = private_post(userid)[0]
    personal_posts = get_all_posts(userid)[0]
    private_id = []
    public_id = []
    for item in personal_posts:
        private_id.append(item[0])
    for item in public_posts:
        public_id.append(item[0])
    try:
        if id in public_id:
            position = public_id.index(id)
            prev = position + 1
            return post(public_id[prev])
        else:
            if id in private_id:
                position = private_id.index(id)
                prev = position + 1
                return post(private_id[prev])       
    except Exception as error:
        return f'<h2>An error  has occured </h2><br>{error}<br> <h4>Contact Support For Assistance</h4> <br> <a href="/blog/{id}">Home</a>'

    #  EDIT POST


@app.route('/blog/edit/<int:post_id>/<title>', methods=['GET', 'POST'])
def edit(post_id, title):
    username = session['username']
    userid = session['userid']
    count = len(get_all_posts(userid)[1])
    if request.method == 'POST':
        author =  username
        title = request.form['title']
        content = request.form['content']
        if request.form.getlist('yes'):
            privacy = 'Yes'
        else:
            privacy = "No"
        edit_post(userid,post_id, username, title,content,privacy)
        return post(post_id)
    else:
        content = get_edit_post(userid,post_id,title)
        return render_template('editpost.html', post=content, username=username)


# DELETE POST


@app.route('/blog/delete/<int:id>/<title>')
def delete(id, title):
    userid = session['userid']
    username = session['username']
    delete_post(userid,username, id, title)
    return redirect(url_for('blog'))


@app.route('/play/search', methods=['POST'])
def search_letter():
    letter = request.form['letter']
    phrase = request.form['phrase']
    result = str(search4letters(letter, phrase))
    return render_template('play.html', result=result)


@app.route('/play/lucky_no', methods=['POST', 'GET'])
def lucky():
    guess = int(request.form.get('guess', False))
    response = lucky_number(guess)
    return render_template('play.html', response=response)


@app.route('/play/keygen')
def keygen():
    key = password_gen()
    return render_template('play.html', key=key)


@app.route('/play/bmi', methods=['POST'])
def bmi():
    name = request.form['name']
    weight = int(request.form['weight'])
    height = float(request.form['height'])
    bmi = bmi_calc(name, weight, height)
    return render_template('play.html', bmi=bmi)


if __name__ == '__main__':
    app.run(host='192.168.1.104',debug=True)
