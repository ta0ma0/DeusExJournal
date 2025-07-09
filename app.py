import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'DeusExJournal.db')}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)



import routes
import models

