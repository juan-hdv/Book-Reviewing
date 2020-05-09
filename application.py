import flask
import os, re
import ahocorasick
import numpy as np

from flask import Flask, session, render_template, request,  redirect, url_for 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import timedelta

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
    # If there is an active session for user
    if session.get ("username"): # != None
        username = session['username']
        if not session.get ("books"):
            session["books"] = db.execute("SELECT * FROM books").fetchall()
        return redirect(url_for('books'))
    else:
        return render_template("login.html", msgType="alert-light", #bootstrap alert
                                             msgText="Please type your username and password")
            

@app.route("/login",methods=["POST"])
def login():
    # User POSTed usr/pwd from login template
    username = request.form.get ('username')
    password = request.form.get ('password')
    # Make sure username exist and password is correct
    if db.execute("SELECT * FROM users WHERE usr = :usr AND pass = :pwd", {"usr": username, "pwd":password}).rowcount != 0:
        session["username"] = username
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


@app.route("/books",methods=["GET"])
def books():
    return render_template("books.html",books=None)


@app.route("/books_search",methods=["POST"])
def booksSearch():

    books=[]
    if session.get ("books"):
        books = session["books"]

    searchTermsStr = request.form.get ('searchTerms')
    searchTerms = re.sub ("[^a-z0-9_ ]","",searchTermsStr.lower())
    searchTerms = searchTerms.split (" ")

    searchMode = request.form.get ('searchMode')

    # Optimal search from solution in: 
    # https://stackoverflow.com/questions/34816775/python-optimal-search-for-substring-in-list-of-strings
    '''
    auto = ahocorasick.Automaton() 
    for word in searchTerms:
        auto.add_word(word, word)
    auto.make_automaton()
    '''

    allWords = searchMode == "True"
    matchedBooks = []
    for bk in books:
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
            # find anyWord (OR) or allWords (AND)
            if (not allWords) or (count == 0):
                matchedBooks.append ([{"id":bk.id,"isbn":bk.isbn,"title":bk.title, "author":bk.author,"year":bk.year},matches])

    sortedBooks = []            
    if matchedBooks:
        m = np.array(matchedBooks)
        # Sort indexes
        indexes = np.argsort(m[:,-1])
        # Sort matrix rows by indexes / [::-1,:1:] In inverse order for all rows (-1) and returning only colum 0
        sortedBooks = m[indexes,:][::-1,:1:]
        # Returns a siple list of diccionaries (a non numpy list)
        sortedBooks = sortedBooks[:,0].tolist()
    
    results = len(sortedBooks)
    msg = f"{results} books found. "
    if not results:
        msg +="Change your parameters or search terms and try again"
    return render_template("books.html",books=sortedBooks, searchTerms=searchTermsStr,allWords=allWords, msg=msg)
    #return redirect(url_for("books"))
    
@app.route("/booktab/<string:book_id>",methods=["POST","GET"])
def booktab(book_id):

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": int(book_id)}).fetchone()
    if book is None:
        return render_template("error.html", message="Invalid book number.")
    return render_template("booktab.html",book=book)
    


