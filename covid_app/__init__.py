from flask import Flask

app = Flask(__name__)

from covid_app import routes
