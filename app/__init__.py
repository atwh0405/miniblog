#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask import Flask
from instance.config import config
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from .admin.views import AuthenticatedMenuLink, UnauthenticatedMenuLink, \
	UserView, PostView, CommentView, TagView
import os


bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
myadmin = Admin(name='AT-BLOG', template_mode='bootstrap3')
from .models import User, Post, Comment, Tag
myadmin.add_view(UserView(User, db.session, name='用户管理', endpoint='user-manage'))
myadmin.add_view(PostView(Post, db.session, name='文章管理', endpoint='post-manage'))
myadmin.add_view(CommentView(Comment, db.session, name='评论管理', endpoint='comment-manage'))
myadmin.add_view(TagView(Tag, db.session, name='标签管理', endpoint='tag-manage'))
myadmin.add_link(AuthenticatedMenuLink(name=u'返回', endpoint='main.index'))
myadmin.add_link(UnauthenticatedMenuLink(name=u'登录', endpoint='auth.login'))
path = os.path.join(os.path.dirname(__file__), 'static')
myadmin.add_view(FileAdmin(path, '/static', name='静态文件'))


def create_app(config_name):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py')
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)
	myadmin.init_app(app)
	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint
	from .user import user as user_blueprint
	from .post import post as post_blueprint
	from .admin import admin as admin_blueprint
	from .tag import tag as tag_blueprint
	app.register_blueprint(main_blueprint)
	app.register_blueprint(auth_blueprint, url_prefix='/auth')
	app.register_blueprint(user_blueprint, url_prefix='/user')
	app.register_blueprint(post_blueprint, url_prefix='/post')
	app.register_blueprint(admin_blueprint, url_prefix='/admin')
	app.register_blueprint(tag_blueprint, url_prefix='/tag')
	return app

