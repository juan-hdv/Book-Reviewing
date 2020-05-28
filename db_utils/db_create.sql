/*
Tables 
    books:  a list of books with id, isbn, title, author and year
    users:  a list of system users with id, name, email, user and password
    reviews:a list of reviews. Each review corresponds to a book (id) and is made by an user (id).
            The composed key of this table is made of the keys from tables users and books.

    Some restrictions have been defined for:
        - book year: a year between 1000 and 3000
        - users email: alphanumeric name (plus ._%-), then the @ symbol, then an alphanumeric domain name
        - uisers username: alphanumeric

    Som constrains have been defined for reviews table
        - When a book (id) is deleted/updated, delete/update all the associated reviews (bookId)
        - When a user (id) is deleted/updated, delete/update all the associated reviews (userId)

*/
DROP TABLE reviews;
DROP TABLE books;
DROP TABLE users;
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(13) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    author VARCHAR(64) NOT NULL,
    year INTEGER NOT NULL CHECK (year > 1000 AND year < 3000)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    email VARCHAR(64) NOT NULL CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    usr VARCHAR(10) NOT NULL CHECK (user ~* '^[A-Za-z0-9_-]+$'),
    passw VARCHAR(256) NOT NULL
);

CREATE TABLE reviews (	
    bookId INTEGER NOT NULL,
    userId INTEGER NOT NULL,
    txt VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL,
    PRIMARY KEY (bookId, userId),
    CONSTRAINT reviews_booksId_fkey FOREIGN KEY (bookId) REFERENCES books(id)
    	ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT reviews_usersId_fkey FOREIGN KEY (userId) REFERENCES users(id)
    	ON UPDATE CASCADE ON DELETE CASCADE
)