import flask
import requests
import os, re
import json
import numpy as np

from flask import Flask, session, render_template, request, redirect, url_for 
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
    # If there is an user active session
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
    user = db.execute("SELECT * FROM users WHERE usr = :usr AND pass = :pwd", {"usr": username, "pwd":password}).first()
    if user:
        session["userId"] = user.id
        session["username"] = user.name
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

    # Get the session varaibles for rendering a list of matched books or an empty list (if not matching or first time on the page)
    searchTermsStr = ""
    searchAllWords = False
    searchResults = []
    if session.get ("searchTermsStr"):
        searchTermsStr = session["searchTermsStr"]
        searchAllWords = session["searchAllWords"]
        searchResults = session["searchResults"]

        numResults = len(searchResults)
        msg = f"{numResults} books found. "
        if not numResults:
            msg +="Change your parameters or search terms and try again"
    else: # First access to this page
        msg = "There are thousands of books among which you can find those of your preferences."

    # Render a sorted list of dictionaries - Sorted according to the relevance of the results
    return render_template("books.html",books=searchResults, searchTerms=searchTermsStr,allWords=searchAllWords, msg=msg)


@app.route("/books_search",methods=["POST"])
def booksSearch():

    # Get the list of books from DB, recovered at user login 
    books=[]
    if session.get ("books"):
        books = session["books"]

    allWords = (request.form.get ('searchMode') == "allWords")

    searchTermsStr = request.form.get ('searchTerms')
    searchTerms = re.sub ("[^a-z0-9_ ]","",searchTermsStr.lower())
    searchTerms = searchTerms.split (" ")

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

    # Set the appropiate session variables
    session["searchTermsStr"] = searchTermsStr
    session["searchAllWords"] = allWords
    session["searchResults"] = sortedBooks
    
    return redirect(url_for('books'))

    
@app.route("/booktab/<int:bookId>",methods=["GET"])
def booktab(bookId):
    # Get book info, including the user review and rating if present
    book = db.execute("SELECT * FROM books as b \
        LEFT JOIN reviews as r ON r.bookId = b.id AND r.userId = :userId \
        WHERE b.id = :bookId",{"userId":session["userId"],"bookId":bookId}).fetchone()

    # book = db.execute("SELECT * FROM books WHERE id = :id", {"id": bookId}).fetchone()
    if book is None:
        raise Exception(f'Invalid book number: {bookId}')

    userReview = {"text": book.txt, "rating": book.rating}
    goodreadsRating = getGoodreadsRating (book.isbn)

    return render_template("booktab.html",book=book, goodreadsRating=goodreadsRating, userReview=userReview)

def getGoodreadsRating (isbn):
    # Get gooreads book rating
    headers = {"content-type": "application/json"}
    r = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ZR0Vn8jaLessV6NJqMdPTA", "isbns": isbn}, headers=headers)

    if r.status_code == 200:
        bookInfo= r.json()
         # Get the firts (the only) element in list: a dict.
        bookInfo = bookInfo['books'].pop()
        goodreadsRating = {"work_ratings_count":bookInfo["work_ratings_count"], "average_rating":bookInfo["average_rating"] }
    else:
        # Service unavailable
        goodreadsRating = {"work_ratings_count":-1, "average_rating":-1 }
    return goodreadsRating


@app.route("/book_review",methods=["POST"])
def bookReview():
    # PRE: user_rating cannot be None / user_rating can be "" 
    userId = session["userId"]
    bookId = request.form.get ('book_id')
    userReview = request.form.get ('user_review')
    userRating = request.form.get ('user_rating')

    # DO A POSTGRESS UPSERT
    db.execute ("INSERT INTO reviews (bookId,userId,txt,rating) VALUES (:bookId, :userId, :userReview, :userRating) \
        ON CONFLICT (bookId, userId) DO \
        UPDATE SET (txt,rating) = (:userReview, :userRating)",
        {"bookId":bookId, "userId":userId, "userReview":userReview, "userRating":userRating})
    db.commit()

    return redirect (url_for("booktab",bookId=bookId))
