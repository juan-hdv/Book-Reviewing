import os, re, ahocorasick
import numpy as np

from flask import Flask, session, render_template, request,  redirect, url_for 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"): 
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=["GET"])
def index ():
    username = session.get('username')
    # If there is an active session for user
    if username: # != None
        return redirect(url_for('books'))
    else:
        return render_template("login.html", msgType="alert-light", #bootstrap alert
                                             msgText="Please type your username and password")
            

@app.route("/",methods=["POST"])
def login():
    # User POSTed usr/pwd from login template
    username = request.form.get ('username')
    password = request.form.get ('password')
    # Make sure username exist and password is correct
    if db.execute("SELECT * FROM users WHERE usr = :usr AND pass = :pwd", {"usr": username, "pwd":password}).rowcount != 0:
        session["username"] = username
        #session.commit()
        return redirect(url_for("index"))
    return render_template("login.html", msgType="alert-danger", #bootstrap alert
                                         msgText="Invalid user or password! Try again.")


@app.route("/logout",methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/register",methods=["GET"])
def register():   	
    return render_template("registration.html")

@app.route("/saveRegistration",methods=["POST"])
def saveRegistration():
	# get fields
    name = request.form.get ('name')
    email = request.form.get ('email')
    user = request.form.get ('user')
    password = request.form.get ('password')

    # Make sure username does not exist
    if db.execute("SELECT * FROM users WHERE usr = :usr", {"usr": user}).rowcount != 0:
        return render_template("error.html", message="Username is not available. Please use a diffent username.")
    db.execute("INSERT INTO users (name, email, usr, pass) VALUES (:name, :email, :user, :password)",
            {"name": name, "email": email, "user":user, "password":password})
    db.commit()
    return render_template("login.html", msgType="alert-success", #bootstrap alert
                                         msgText="Please type your username and password")


@app.route("/books",methods=["POST"])
def books():
    return render_template("books.html",books=books)


@app.route("/books_search",methods=["POST"])
def booksSearch():
    #
    # Optimal search from solution in: 
    # https://stackoverflow.com/questions/34816775/python-optimal-search-for-substring-in-list-of-strings
    #
    searchTerms = request.form.get ('search_terms')
    searchTerms = re.sub ("[^a-z0-9_ ]","",searchTerms.lower())
    searchTerms = searchTerms.split (" ")
    '''
    auto = ahocorasick.Automaton() 
    for word in searchTerms:
        auto.add_word(word, word)
    auto.make_automaton()
    '''

    books = db.execute("SELECT * FROM books").fetchall()
    matchedBooks = []
    for bk in books:
        lbk = list(bk)
        lbk.append(0) 
        allWords = False
        matches = 0 
        matchesPrev = 0 
        count = len (searchTerms)
        # Count matches for presenting more relevant results firts
        for st in searchTerms:
            if st in bk.isbn.lower():
                matches+=1
            if st in bk.title.lower():
                matches+=1
            if st in bk.author.lower():
                matches+=1
            if matchesPrev < matches:
                count-=1
                matchesPrev = matches
        if matches:
            # find AnyWord (OR) or AllWords (AND)
            if (not allWords) or (count == 0):
                lbk[5] = matches
                matchedBooks.append (lbk)

    m = np.array(matchedBooks)
    # Sort indexes
    indexes = np.argsort(m[:,-1])
    # Sort matrix rows by indexes, in inverse orden (-1)
    sortedBooks = m[indexes,:][::-1]
    return render_template("books.html",books=sortedBooks.tolist())
    #return redirect(url_for("books"))
    
@app.route("/booktab/<string:book_id>",methods=["POST","GET"])
def booktab(book_id):

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": int(book_id)}).fetchone()
    if book is None:
        return render_template("error.html", message="Invalid book number.")
    return render_template("booktab.html",book=book)
    


