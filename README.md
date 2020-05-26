# Project 1
# Web Programming with Python and JavaScript

* Set the following variables in ~/.profile*

# Python development variables
export FLASK_APP="application.py"
export FLASK_DEBUG=1
export FLASK_ENV="development"
export DATABASE_URL='postgres://svvoceyhxqbdas:b7e1045e4df54f881134a71338ce3f0d62508ae2c2fd43155689dbb219ac747b@ec2-18-233-137-77.compute-1.amazonaws.com:5432/d2lj9lb32ova47'



# You have to set an enviroment for Python 3 and then install Requests
python3 -m venv my-project-env
source my-project-env/bin/activate
pip install requests