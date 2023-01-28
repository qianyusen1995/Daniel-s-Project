# encoding: utf-8
import os
import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:install123!@localhost:3306/movie"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SECRET_KEY"] = "ERHJKL;HDFHJKL;"
app.config["REDIS_URL"] = "redis://127.0.0.1:6379/0"

rd = FlaskRedis(app)

# 文件上传路径
# windows
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static\\uploads\\")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static\\uploads\\users\\")
# linux
# app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")
# app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")

app.debug = False
db = SQLAlchemy(app)


from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404