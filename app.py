######################################
# author Wei Wei <wei0496@bu.edu> 
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import numpy as np

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'YOURPASSWORD'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()
Album_id = 0


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users") 
    return cursor.fetchall()

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0] )
    user.is_authenticated = request.form['password'] == pwd 
    return user

'''
A new page looks like this:
@app.route('new_page_name')     <label for="comment">Enter the comments for the photo(format: photoid comment):</label>
        <input type="comment" name="comment" /><br />
def new_page_function():
    return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
	       <a href='/'>Go Back</a>
               '''
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return flask.redirect(flask.url_for('home')) #protected is a function defined in this file

    #information did not match
    return "<a href='/login'>Try again</a>\    </br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
    try:
        first_name=request.form.get('first_name')
        last_name= request.form.get('last_name')
        DOB = request.form.get('DOB')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        email=request.form.get('email')
        password=request.form.get('password')
    except:
        print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        cursor.execute("INSERT INTO Users (email, password, first_name, last_name, DOB, hometown, gender) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(email, password, first_name, last_name, DOB, hometown, gender))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('home.html', name=first_name, message='Account Created!')
    else:
        print "couldn't find all tokens"
        return flask.redirect(flask.url_for('register'))

#Returns all the tags of this photo
def getAllTags(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM taged_by WHERE Photo_id = '{0}'".format(pid))
    return cursor.fetchall()

#Returns all the tag for this user
def getUsrTags(uid):
    result = []
    p = getPhotosfrom(uid)
    cursor = conn.cursor()
    cursor.execute("SELECT T.description, COUNT(T.Photo_id) AS frequency FROM taged_by T WHERE T.Photo_id in (SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{0}') GROUP BY T.description ORDER BY frequency DESC LIMIT 5".format(uid))
    info = cursor.fetchall()
    print(info)
    return info

#Returns all the tags for this user
def getUsrTags1(uid):
    result = []
    p = getPhotosfrom(uid)
    cursor = conn.cursor()
    cursor.execute("SELECT T.description, COUNT(T.Photo_id) AS frequency FROM taged_by T WHERE T.Photo_id in (SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{0}') GROUP BY T.description ORDER BY frequency".format(uid))
    info = cursor.fetchall()
    return info

#Returns the photo which the user may like
def getalsolike(uid):
    lst = []
    result1 = []
    result = get5Tags(uid)
    cursor = conn.cursor()
    cursor.execute("SELECT P.imgdata, P.caption, T.Photo_id, COUNT(T.description) AS x, SUM(CASE WHEN T.description = '{0}' THEN 1 ELSE 0 END + CASE WHEN T.description = '{1}' THEN 1 ELSE 0 END + CASE WHEN T.description = '{2}' THEN 1 ELSE 0 END + CASE WHEN T.description = '{3}' THEN 1 ELSE 0 END + CASE WHEN T.description = '{4}' THEN 1 ELSE 0 END) AS matches FROM taged_by T, Photos P WHERE T.Photo_id = P.Photo_id AND T.Photo_id NOT IN (SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{5}') GROUP BY T.Photo_id ORDER BY matches DESC, x ASC LIMIT 10".format(result[0],result[1],result[2],result[3],result[4], uid))
    info = cursor.fetchall()
    for i in range(len(info)):
        print(info[i][2],info[i][3],info[i][4])
        if owns(uid, info[i][2]):
            lst.append(i)
    print(lst)
    return info

#Returns the 5 most popular tag for this user
def get5Tags(uid):
    result = []
    p = getPhotosfrom(uid)
    cursor = conn.cursor()
    cursor.execute("SELECT T.description, COUNT(T.Photo_id) AS frequency FROM taged_by T WHERE T.Photo_id in (SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{0}') GROUP BY T.description ORDER BY frequency DESC LIMIT 5".format(uid))
    info = cursor.fetchall()
    for i in range(0,5):
        try:
            result.append(info[i][0])
        except:
            result.append('')
    print(result)
    return result

#Returns the photo id the user has
def getPhotosfrom(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{0}'".format(uid))
    return cursor.fetchall()

#Returns if the user owns the photo
def owns(uid, pid):
    cursor = conn.cursor()
    cursor.execute("SELECT P.photo_id FROM Photos P WHERE P.photo_id = '{0}' AND P.photo_id in (SELECT P.photo_id FROM Photos P, Albums A WHERE P.Album_id = A.Album_id AND A.User_id = '{1}')".format(pid, uid))
    info = cursor.fetchall()
    if not info:
        return False
    else:
        return True

#Returns the recommended tag
def getTags(recommendation):
    result = [0] * len(recommendation)
    for i in range((len(recommendation))):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(Photo_id) FROM taged_by WHERE description = '{0}'".format(recommendation[i]))
        info = cursor.fetchall()[0][0]
        result[i] = info
    print(result)
    return recommendation[result.index(max(result))]

#Gets the Users in the system
def getUsers(email):
    cursor = conn.cursor()
    cursor.execute("SELECT email, first_name, last_name, DOB, hometown, gender FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchall()

def getUsersPhotos(album_id):
    print('getusersphotos')
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, caption, photo_id FROM Photos P WHERE Album_id = '{0}'".format(album_id))
    return cursor.fetchall()

#search for photos with pid
def getPhotos(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P WHERE P.photo_id = '{0}'".format(pid))
    return cursor.fetchall()

#search for photos with tag and uid
def getTagPhotos(tag, uid):
    cursor = conn.cursor()
    cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P, taged_by T WHERE T.description = '{0}' AND T.Photo_id = P.photo_id AND P.Album_id in (SELECT Album_id FROM Albums A WHERE A.user_id = '{1}')".format(tag, uid))
    return cursor.fetchall()

#get all the comments and uid from Photo_id
def getComments(photo_id):
    cursor = conn.cursor()
    cursor.execute("SELECT C.text1, L.user_id, C.dates FROM Comments C, leaves L WHERE C.Photo_id = '{0}' AND C.Comment_id = L.Comment_id".format(photo_id))
    info = cursor.fetchall()
    return info

#get all the likes and uid from Photo_id
def getLikes(photo_id):
    cursor = conn.cursor()
    cursor.execute("SELECT U.email, L.user_id FROM likes L, Users U WHERE U.user_id = L.user_id AND L.Photo_id = '{0}'".format(photo_id))
    return cursor.fetchall()

#Returns the top5 most popular tags
def getPopularTags():
    cursor = conn.cursor()
    cursor.execute("SELECT description, count(*) as frequency FROM taged_by GROUP BY description ORDER BY count(*) DESC")
    return cursor.fetchall()

#Get all the photos from the database
def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P")
    return cursor.fetchall()

#search for all photos with the tag
def getTagallPhotos(tag):
    newtag = tag.split(" ")
    cursor = conn.cursor()
    lst = []
    id = []
    cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P, taged_by T WHERE T.description = '{0}' AND T.Photo_id = P.photo_id".format(newtag[0]))
    result0 = cursor.fetchall()
    if len(newtag) == 1:
        return result0
    for i in range(len(result0)):
        id.append(result0[i][2])
    cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P, taged_by T WHERE T.description = '{0}' AND T.Photo_id = P.photo_id".format(newtag[1]))
    result1 = cursor.fetchall()
    for row in result1:
        if row[2] in id:
            lst.append(row)
    if len(newtag) == 2:
        return lst 
    for i in range(2,len(newtag)):
        cursor.execute("SELECT P.imgdata, P.caption, P.photo_id FROM Photos P, taged_by T WHERE T.description = '{0}' AND T.Photo_id = P.photo_id".format(newtag[i]))
        result = cursor.fetchall()
        for row in result:
            if row[2] in id:
                lst.append(row)
    return lst

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
        #this means there are greater than zero entries with that email
        return False
    else:
        return True

def isTagUnique(tag):
    #use this to check if a tag has already been used
    cursor = conn.cursor()
    if cursor.execute("SELECT description FROM Tags WHERE description ='{0}'".format(tag)):
        return False
    else:
        return True

#Checks the usr activity
def checkactivity():
    cursor = conn.cursor()
    cursor.execute("CREATE TEMPORARY TABLE temp1 AS (SELECT U.User_id, COUNT(P.photo_id) AS occurance FROM Photos P, Users U, ALbums A WHERE P.Album_id = A.Album_id AND A.user_id = U.User_id GROUP BY U.User_id)")
    cursor.execute("CREATE TEMPORARY TABLE temp2 AS (SELECT U.User_id, COUNT(L.Comment_id) AS occurance FROM Users U, leaves L WHERE L.user_id = U.User_id GROUP BY U.User_id)")
    cursor.execute("CREATE TEMPORARY TABLE temp3 AS (SELECT User_id, SUM(Occurance) AS x FROM (SELECT * FROM temp1 UNION ALL (SELECT * FROM temp2))s group by User_id ORDER BY x)")
    cursor.execute(" SELECT T.User_id, x, U.first_name, U.last_name, U.email FROM Users U, Temp3 T WHERE U.user_id = T.User_id ORDER BY x DESC LIMIT 10")
    info = cursor.fetchall()
    cursor.execute("DROP TABLE temp1")
    cursor.execute("DROP TABLE temp2")
    cursor.execute("DROP TABLE temp3")
    return info

'''
def checkactivity():
    x = 0
    notactiveuser = []
    result = []
    lst = [0] * 500
    cursor = conn.cursor()
    cursor.execute("SELECT U.User_id, COUNT(P.photo_id) AS occurance FROM Photos P, Users U, ALbums A WHERE P.Album_id = A.Album_id AND A.user_id = U.User_id GROUP BY U.User_id")
    info = cursor.fetchall()
    for row in info:
        lst[row[0]] = row[1]
    cursor.execute("SELECT U.User_id, COUNT(L.Comment_id) AS occurance FROM Users U, leaves L WHERE L.user_id = U.User_id GROUP BY U.User_id")
    info1 = cursor.fetchall()
    for row in info1:
        lst[row[0]] += row[1]
    for i in range(10):
        if max(lst) == 0:
            x = i
            break
        result.append(lst.index(max(lst)))
        lst[result[i]] = 0
        
    cursor.conn.cursor()
    for i in range len(result):
        cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(result[i]))

    return result
    '''

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    cursor.execute("SELECT first_name, last_name, DOB, hometown, gender, email FROM Users WHERE email = '{0}'".format(flask_login.current_user.id))
    profile = cursor.fetchall()
    return render_template('profile.html', name = profile, message = profile[0][0])

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET'])
@flask_login.login_required
def upload_file():
    # The method is GET so we return a  HTML form to upload the a photo.
     #render_template('upload.html') 
    return ''' <!doctype html>
        <title>Upload new Picture</title>
        <h1>Upload new Picture</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file></p>
        <label for="caption">Please caption:</label>
        <input type=text name='caption' required='true' /><br />
        <label for="tag">Please tag this photo:</label>
        <input type=text name='tag' /><br />
        <input type=submit value=Upload>
        </form></br>
    <a href='/'>Home</a>'''

@app.route('/upload', methods=['POST'])
@flask_login.login_required
def upload_files():
#end photo uploading code 
    global Album_id
    uid = getUserIdFromEmail(flask_login.current_user.id)
    imgfile = request.files['file']
    photo_data = base64.standard_b64encode(imgfile.read())
    cursor = conn.cursor()
    caption = request.form.get('caption')
    tag = request.form.get('tag')
    print(Album_id)
    cursor.execute("INSERT INTO Photos (imgdata, Album_id, caption) VALUES ('{0}','{1}','{2}')".format(photo_data,Album_id,caption))
    cursor.execute("SELECT last_insert_id()")
    #cursor.execute("SELECT C.Comment_id FROM Comments C WHERE C.Photo_id = '{0}' AND C.text1 = '{1}'".format(newcomment[0],newcomment[1]))
    info = cursor.fetchone()
    photo_id = info[0]
    if tag != '':
        if isTagUnique(tag):
            cursor.execute("INSERT INTO Tags (description) VALUES ('{0}')".format(tag))
            conn.commit()
        cursor.execute("INSERT INTO taged_by (Photo_id, description) VALUES ('{0}','{1}')".format(photo_id,tag))
        conn.commit()
    return render_template('albums.html', message='Photo uploaded!', photos=getUsersPhotos(Album_id) )

#home page
@app.route("/home", methods=['GET'])
def home():
    cursor.execute("SELECT first_name, last_name, DOB, hometown, gender, email FROM Users WHERE email = '{0}'".format(flask_login.current_user.id))
    profile = cursor.fetchall()
    return render_template('home.html', name = profile[0][0])

#add friends
@app.route("/addfriends", methods=['GET','POST'])
@flask_login.login_required
def addfriend():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        try:
            email1 = request.form.get('email1')
            email=request.form.get('email')
        except:
            print "couldn't find all tokens"
            return flask.redirect(flask.url_for('addfriend'))
        if email1 != '':
            info = getUsers(email1)
            if not info:
                return render_template('addfriends.html', name = 'The User you are looking for does not exists, try another email')
            return render_template('addfriends.html', message = getUsers(email1))
        elif email != '':
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE Users.email = '{0}'".format(email))
            info = cursor.fetchmany()
            if not info:
                return render_template('addfriends.html', name = 'The email you are looking for does not exists, try another email')
                '''
                    <!doctype html>
                    <body>
                        <div id="content">
                            <form method="post" action="">
                                <h1>The email you are looking for does not exists</h1>
                                <label for="email">Enter your friend's email:</label>
                                <input type="email" name="email" /><br />
                                <input type="submit" />
                            </form>
                        </div>
                    </body>

                    <ul>
                    <li><a href='/home'>Home</a></li>
                    </ul>
                    '''
            try:
                cursor.execute("INSERT INTO Friends (User_id, f_id) VALUES ('{0}','{1}')".format(uid,info[0][0]))
                conn.commit()
                cursor.execute("INSERT INTO Friends (User_id, f_id) VALUES ('{0}','{1}')".format(info[0][0],uid))
                conn.commit()
            except:
                return render_template('addfriends.html', name = 'You have already been friends or you can not be friends with yourself') 
                '''
                    <!doctype html>
                    <body>
                        <div id="content">
                            <form method="post" action="">
                                <h1>You have already been friends</h1>
                                <label for="email">Enter your friend's email:</label>
                                <input type="email" name="email" /><br />
                                <input type="submit" />
                            </form>
                        </div>
                    </body>

                    <ul>
                    <li><a href='/home'>Home</a></li>
                    </ul>
                    '''
            return render_template('home.html', message='Friend added!')
    return render_template('addfriends.html')
    '''
    <!doctype html>
    <body>
        <div id="content">
            <form method="post" action="">
                <label for="email">Enter your friend's email:</label>
                <input type="email" name="email" /><br />
                <input type="submit" />
            </form>
        </div>
    </body>

    <ul>
    <li><a href='/home'>Home</a></li>
    </ul>
    '''

#list friends
@app.route("/listfriends", methods=['GET'])
@flask_login.login_required
def listfriend():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT u.first_name, u.last_name, u.email FROM Friends f, Users u WHERE u.user_id = f.f_id AND f.user_id = '{0}'".format(uid))
    info = cursor.fetchall()

    return render_template('listfriends.html', message=info)

#Albums
@app.route("/listalbums", methods =['GET'])
@flask_login.login_required
def listalbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT Album_id, name, date_of_creation FROM Albums A WHERE A.user_id = '{0}'".format(uid))
    info = cursor.fetchall()

    return render_template('listalbums.html', message=info, tags = getUsrTags1(uid))

@app.route("/listalbums", methods =['POST'])
@flask_login.login_required
def addordeletealbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            name=request.form.get('name')
            name1 = request.form.get('name1')
        except:
            print "couldn't find all tokens"
            return flask.redirect(flask.url_for('listalbums'))
    if name != '':
        try:
            cursor.execute("INSERT INTO Albums (user_id, name) VALUES('{0}','{1}')".format(uid, name))
            conn.commit()
            cursor.execute("SELECT Album_id, name, date_of_creation FROM Albums A WHERE A.user_id = '{0}'".format(uid))
            info = cursor.fetchall()
            return render_template('listalbums.html', name = 'album added!', message = info, tags = getUsrTags1(uid))
        except:
            cursor.execute("SELECT Album_id, name, date_of_creation FROM Albums A WHERE A.user_id = '{0}'".format(uid))
            info = cursor.fetchall()
            return render_template('listalbums.html', name = 'album already exists!', message = info, tags = getUsrTags1(uid))
    elif name1 != '':
        cursor.execute("DELETE FROM Albums WHERE name = '{0}'".format(name1))
        conn.commit()
        cursor.execute("SELECT Album_id, name, date_of_creation FROM Albums A WHERE A.user_id = '{0}'".format(uid))
        info = cursor.fetchall()
        return render_template('listalbums.html', name = 'album deleted!', message = info, tags = getUsrTags1(uid))

#add photos

@app.route("/albums", methods =['GET'])
@flask_login.login_required
def albums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    try:
        Aid = request.args['album_id']
        global Album_id 
        Album_id = Aid
        print(Album_id)
        return render_template('albums.html', photos = getUsersPhotos(Album_id))
        # return render_template('albums.html', photos = getUsersPhotos(Album_id), tags = getUsrTags1(uid))
    except:
        try:
            tag = request.args['tag']
            print(tag)
            # global Album_id
            return render_template('albums.html', photos = getTagPhotos(tag, uid))
        except:
            pid = request.args['photo_id']
            return render_template('albums.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)))

@app.route("/albums", methods =['POST'])
@flask_login.login_required
def album():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    try:
        caption = request.form.get('caption')
        tag = request.form.get('tag')
        recommendation = request.form.get('recommendation')
        pid = request.form.get('pid')
    except:
        print "couldn't find all tokens"
        return flask.redirect(flask.url_for('albums'))
    global Album_id
    if caption != '':
        if owns(uid,caption) == False:
            return render_template('albums.html', photos = getUsersPhotos(Album_id), message = 'This photo does not belongs to you or does not exist!')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Photos WHERE Photo_id = '{0}'".format(caption))
        conn.commit()
        return render_template('albums.html', photos = getUsersPhotos(Album_id), message = 'Photo deleted!')
    elif tag != '':
        newtag = tag.split(" ")
        cursor = conn.cursor()
        if owns(uid, newtag[0]) == False:
            return render_template('albums.html', photos = getUsersPhotos(Album_id), message = 'This photo does not belongs to you or does not exist!')
        if isTagUnique(newtag[1]):
            cursor.execute("INSERT INTO Tags (description) VALUES ('{0}')".format(newtag[1]))
            conn.commit()
        cursor.execute("INSERT INTO taged_by (Photo_id, description) VALUES ('{0}','{1}')".format(newtag[0],newtag[1]))
        conn.commit()
        return render_template('albums.html', photos = getUsersPhotos(Album_id), message = 'Photo taged!')
    elif recommendation != '':
        newrecommendation = recommendation.split(",")
        return render_template('albums.html', name = getTags(newrecommendation))
    elif pid != '':
        return render_template('albums.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)))

#Photosearch
@app.route("/photosearch", methods=['GET'])
@flask_login.login_required
def photosearch():
    try:
        tag = request.args['tag']
        return render_template('photosearch.html', message = 'Here are the photos with tag ' + str(tag), photos = getTagallPhotos(tag))
    except:
        try:
            pid = request.args['photo_id']
            return render_template('photosearch.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)), tags = getAllTags(pid))
        except:
            return render_template('photosearch.html', message = 'welcome to photosearch, you can search photos by tags, Here are the most popular tags', name = getPopularTags())

@app.route("/photosearch", methods =['POST'])
@flask_login.login_required
def photosearch2():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    global Album_id
    if request.method == 'POST':
        try:
            tag = request.form.get('tag')
            comment = request.form.get('comment')
            like = request.form.get('like')
            pid = request.form.get('pid')
        except:
            print "couldn't find all tokens"
            return flask.redirect(flask.url_for('photosearch'))
    if tag != '':
        return render_template('photosearch.html', message = 'Here are the photos with tag ' + str(tag), photos = getTagallPhotos(tag))
    elif comment != '':
        newcomment = comment.split(",")
        if owns(uid, newcomment[0]):
            return render_template('photosearch.html', message = 'You can not comment your own photos!', photos = getUsersPhotos(Album_id))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Comments (Photo_id, text1) VALUES ('{0}','{1}')".format(newcomment[0], newcomment[1]))
        conn.commit()
        cursor.execute("SELECT C.Comment_id FROM Comments C WHERE C.Photo_id = '{0}' AND C.text1 = '{1}'".format(newcomment[0],newcomment[1]))
        info = cursor.fetchone()
        commentid = info[0]
        cursor.execute("INSERT INTO leaves (Comment_id, user_id) VALUES ('{0}','{1}')".format(commentid, uid))
        conn.commit()
        return render_template('photosearch.html', message = 'Comment added!', photos = getPhotos(newcomment[0]))
    elif like != '':
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Likes (user_id, Photo_id) VALUES ('{0}','{1}')".format(uid, like))
            conn.commit()
        except:
            return render_template('photosearch.html', message = 'You already liked this photo or this photo does not exist', photos = getUsersPhotos(Album_id))
        return render_template('photosearch.html', message = 'Like added!')
    elif pid != '':
        return render_template('photosearch.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)), tags = getAllTags(pid))

#VisitorPhotosearch
@app.route("/visitorphotosearch", methods=['GET'])
def visitorphotosearch():
    try:
        pid = request.args['photo_id']
        return render_template('visitorphotosearch.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)), tags = getAllTags(pid))
    except:
        return render_template('visitorphotosearch.html', message='welcome to photosearch, you can search photos by tags, or browse all the photos')

@app.route("/visitorphotosearch", methods =['POST'])
def visitorphotosearch2():
    global Album_id
    if request.method == 'POST':
        print('post method')
        try:
            tag = request.form.get('tag')
            comment = request.form.get('comment')
            pid = request.form.get('pid')
        except:
            print "couldn't find all tokens"
            return flask.redirect(flask.url_for('visitorphotosearch'))
    print('get ' + str(tag))
    if tag != '':
        return render_template('visitorphotosearch.html', message = 'Here are the photos with tag ' + str(tag), photos = getTagallPhotos(tag))
    elif comment != '':
        newcomment = comment.split(",")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Comments (Photo_id, text1) VALUES ('{0}','{1}')".format(newcomment[0], newcomment[1]))
        conn.commit()
        cursor.execute("SELECT last_insert_id()")
        #cursor.execute("SELECT C.Comment_id FROM Comments C WHERE C.Photo_id = '{0}' AND C.text1 = '{1}'".format(newcomment[0],newcomment[1]))
        info = cursor.fetchone()
        commentid = info[0]
        cursor.execute("INSERT INTO leaves (Comment_id, user_id) VALUES ('{0}','{1}')".format(commentid, 0))
        conn.commit()
        return render_template('visitorphotosearch.html', message = 'Comment added!')
    elif pid != '':
        return render_template('visitorphotosearch.html', photos = getPhotos(pid), comments = getComments(pid), likes = getLikes(pid), length = len(getLikes(pid)), tags = getAllTags(pid))


#Browse all photos
@app.route("/allphotos", methods=['GET'])
def allphotos():
    return render_template('photosearch.html', message = 'Here are all the photos!', photos = getAllPhotos())

#Browse all for visitors
@app.route("/visitorallphotos", methods=['GET'])
def visitorallphotos():
    return render_template('visitorphotosearch.html', message = 'Here are all the photos!', photos = getAllPhotos())

#Check user activity
@app.route("/usract", methods=['GET'])
def usract():
    return render_template('home.html', message = 'Here are the top 10 active users! (If less than 10 Users are displayed, that means all other users not listed here have zero contribution)', activity = checkactivity())

#You may also like functionality 
@flask_login.login_required
@app.route("/alsolike", methods=['GET'])
def alsolike():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('photosearch.html', photos = getalsolike(uid), message = "These are the photos you may like")

#default page  
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    #this is invoked when in the shell  you run 
    #$ python app.py 
    app.run(port=5000, debug=True)
