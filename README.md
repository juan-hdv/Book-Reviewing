# PROJECT 1 - Web Programming with Python and JavaScript

**Author:** 			Juan Gabriel Mejía

**Date (yyyy-mm-dd):**	2020-05-25


## Environment Variables

 Before running this project, some environment variables must be set.
 For Ubuntu, set the following variables in ~/.profile ()

 	# Python development variables
	export FLASK_APP="application.py"
	export FLASK_DEBUG=1
	export FLASK_ENV="development"
	export DATABASE_URL='postgres://svvoceyhxqbdas:b7e1045e4df54f881134a71338ce3f0d62508ae2c2fd43155689dbb219ac747b@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d2lj9lb32ova47'


## Create an Enviroment 

 Before running this project, an Environment must be set for Python 3 and requirements.txt must be then installed

 To do so, follow this steps:
	python3 -m venv my-project-env
	source my-project-env/bin/activate
	pip install requests

## Project files and description

* db_ultils/
  * db_create.sql:  SQL for creating the databse schema. Three tables: books, users and reviews, being reviews a relationship between users and books. 
  * import.py:      Import into your PostgreSQL database all the books from the file 'books.csv'
* static/
  * css/
    * main.css: 	the particular styles for the projects. It is generated from main.scss
    * main.scss     a Sass file corresponding to the main.css
  * img/
  	* book-half.svg:a Scalable Vector Graphics (svg) for the site logo.
  * js/
  	* main.js: 		jquery actions for selecting and unselecting the stars for the book rating.
  * templates/
  	* books.html: 	the home page where books can be searched and listed.  	
  	* booktab.html: the page where a single booktab is showed, including book info, gooreadings rating and user reviews and ratings.
  	* http_error403.html: error page for 403 error (Forbiden)
  	* http_error404.html: error page for 404 error (Page Not Found)
  	* layout.html: 	root template from which the others inherit. 
  	* login.html: 	login page, for capturing user an d password.
  	* registration.html: page where a new user can give info for registering name, email, username and password.
* .gitignore: 		Git file for ignoring other files.
* application.py: 	the main program file where all the Flask routes and python processes are developed.
* security.py: 		passlib functions for crypting and checking encrypted password (encrypt_password, check_encrypted_password). The password must be cypted before being saved to database; and password given by an user must be check against the crypted password in the database, before being granted acccess.
* README.md: 		this file.
* requirements.txt: all the packages that must be installed before running this project. Use: pip -install requirements.txt


