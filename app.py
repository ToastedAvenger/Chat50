import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_socketio import SocketIO
from werkzeug.security import check_password_hash, generate_password_hash
import string
import random

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
socketio = SocketIO(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///chat50.db")
urls = db.execute("SELECT sub_url FROM rooms")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Default Webpage"""

    return redirect('/public')

"""REGISTER / LOGIN"""
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            print()
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    print("hello")
    if request.method == "POST":
        display_name = request.form.get("display_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmpass")

        # Get list of users from database
        userdb = db.execute("SELECT username FROM users")

        # Ensures that all fields are filled
        if not display_name:
            flash("Invalid Name!", 'error')
            return redirect("/register")
        if username.islower() == False or ' ' in username:
            flash("Invalid username! username should not contain uppercase letters and spaces")
            return redirect("/register")
        if not password or confirm_password != password:
            flash("Invalid password or passwords don't match")
            return redirect("/register")

        # Check if username already exists in database
        if any(user.get('username') == username for user in userdb):
            return apology("Username is taken. Enter another username.", 400)

        # Finally registers the new user
        else:
            db.execute("INSERT INTO users (username, hash, display_name) VALUES(?, ?, ?)", username, generate_password_hash(password=password), display_name)
            return redirect("/")
    return render_template("register.html")


"""PERSONAL ACCOUNT"""
@app.route("/password", methods = ["GET", "POST"])
@login_required
def change_password():
    """Change Password of current user"""

    #Render default page for password
    if request.method == "GET":
        return render_template("password.html")

    # Change password mechanism
    elif request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure old password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            return apology("incorrect old password", 403)

        newpassword = request.form.get("newpassword")
        confirm_password = request.form.get("confirmpass")

        # Ensure new password and confirm password match
        if not newpassword or confirm_password != newpassword:
            return apology("Password don't match.", 403)

        # Updates the database with new password
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(password=newpassword), session["user_id"])
        return redirect("/")

@app.route("/public", methods = ["GET", "POST"])
@login_required
def public_rooms():
    """Display all the rooms that are set to public"""
    if request.method == "GET":
        room_info = db.execute("SELECT * FROM rooms WHERE type = 'public'")
        return render_template("public.html", room_info=room_info)

@app.route("/private", methods = ["GET", "POST"])
@login_required
def private_rooms():
    """Display all the rooms that are set to private"""
    if request.method == "GET":
        room_info = db.execute("SELECT * FROM rooms WHERE type = 'private'")
        return render_template("private.html", room_info=room_info)


@app.route("/yours", methods = ["GET", "POST"])
@login_required
def your_rooms():
    """Display all the rooms that are created by the user"""
    if request.method == "GET":
        room_info = db.execute("SELECT * FROM rooms WHERE host_user = (SELECT username FROM users WHERE id = ?)", session["user_id"])
        return render_template("yours.html", room_info=room_info)

@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    """Function to Create a room"""
    if request.method == "GET":
        return render_template("create.html")
    else:
        # Creating room mechanism 
        room_name = request.form.get("room_name")
        room_type = request.form.get("room_type")
        password = request.form.get("password")
        max_users = request.form.get("max_users")

        # Valid input check
        if not room_name or room_name.isspace():
            flash("Invalid room name.")
            return redirect("/create")
        
        if room_type == "public":
            visible = 1
            password = None
        elif room_type == "private":
            if not password:
                flash("Invalid password.")
                return redirect("/create")
            password = generate_password_hash(password=password)
        else:
            flash("Invalid room type.")
            return redirect("/create")
        
        if not max_users:
            flash("Invalid number of people.")
            return redirect("/create")
        # Create url for room and also check if it already exist in database
        urls = db.execute("SELECT sub_url FROM rooms")
        while True:
            sub_url = ''.join(random.choices(string.ascii_letters, k=4))+"-"+''.join(random.choices(string.ascii_letters, k=4))
            if any(url.get('sub_url') == sub_url for url in urls):
                pass
            else:
                break
        # Finally creates the room
        db.execute("INSERT INTO rooms (room_name, sub_url, no_of_users_MAX, no_of_users_JOINED, type, pass_hash, host_user) VALUES(?, ?, ?, ?, ?, ?,(SELECT username FROM users WHERE id = ?));", room_name, sub_url, max_users, 0, room_type, password, session["user_id"])

        return redirect("/yours")

@app.route("/join", methods = ["POST"])
@login_required
def join():
    """Join room method"""
    room_id = request.form.get("room_id")
    room_info = db.execute("SELECT * FROM rooms WHERE id = ?", room_id)[0]

    # Checks if room is set to private
    if room_info['type'] == "private":
        room_userhost = room_info["host_user"]
        session_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        room_password = request.form.get("password")
        room_password_hash = room_info["pass_hash"]
        if check_password_hash(room_password_hash, room_password) or room_userhost == session_user:
            pass
        else:
            flash("Invalid Password")
            return redirect("/private")

    return redirect(f"/room/{room_info["sub_url"]}")
    
@app.route("/room/<sub_url>", methods = ["GET", "POST"])
@login_required
def room(sub_url):
    """Place where all the magic takes place"""
    if request.method == "GET":
        urls = db.execute("SELECT sub_url FROM rooms")
        if not any(url.get('sub_url') == sub_url for url in urls):
            return apology("Not Found", 404)

        room_info = db.execute("SELECT * FROM rooms WHERE sub_url = ?", sub_url)[0]
        joined_info = db.execute("SELECT joinedId FROM room_users WHERE roomId = ?", room_info["id"])

        if any(session["user_id"] == info.get("joinedId") for info in joined_info):
            pass
        elif room_info["no_of_users_MAX"] == db.execute("SELECT COUNT(*) FROM room_users WHERE roomId = ?", room_info["id"]):
            return apology("Maximum number of people have joined this room. Try Another time")
        else:
            db.execute("INSERT INTO room_users (roomId, joinedId) VALUES(?, ?)", room_info["id"] ,session["user_id"])
            db.execute("UPDATE rooms SET no_of_users_JOINED = (SELECT COUNT(*) FROM room_users WHERE roomId = ?) WHERE id = ?",room_info["id"], room_info["id"])
        location = f"templates/rooms/{sub_url}.html"
        print(os.path.exists(location))
        if os.path.exists(location):
            pass
        else:
            html_content = '{% extends "room.html" %}'
            with open(f"templates/rooms/{sub_url}.html", 'w') as file:
                file.write(html_content)
        
        return render_template(f"rooms/{sub_url}.html")


# for sending and recieving messages
for url in urls:
    @socketio.on('message', namespace=f'/room/{url.get('sub_url')}')
    def handle_message(message, namespace):
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
        socketio.emit('message', f" {username["username"]}\n{message}", namespace=request.namespace)

# For leaving the room
for url in urls:
    @socketio.on('url', namespace=f'/room/{url.get('sub_url')}')
    def leave(url, namespace):
        room_info = db.execute("SELECT * FROM rooms WHERE sub_url = ?", url)[0]
        print(room_info)
        db.execute("DELETE FROM room_users WHERE roomID = ? AND joinedId = ?", room_info["id"] ,session["user_id"])
        db.execute("UPDATE rooms SET no_of_users_JOINED = (SELECT COUNT(*) FROM room_users WHERE roomId = ?) WHERE id = ?",room_info["id"], room_info["id"])
        
        return redirect("/public")


if __name__ == '__main__':
    socketio.run(app)