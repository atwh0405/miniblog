#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy

from flask import Flask
from instance.config import config
from .admin import admin
from .main import main

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()


def create_ap(config_name):
	app = Flask('__name__', instance_relative_config=True)
	app.config.from_pyfile('config.py')
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	db.init_app(app)

	app.register_blueprint(main)
	app.register_blueprint(admin)

	return app

