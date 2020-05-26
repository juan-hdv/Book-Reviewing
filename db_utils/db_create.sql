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