#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, session, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, login_manager
from datetime import datetime
import hashlib
import bleach
import re
from markdown import markdown


class Permissions():
    FOLLOW = 0b00000001
    COMMENT = 0b00000010
    WRITE_ARTICLES = 0b00000100
    MOD_COMMENTS = 0b00001000
    MOD_ARTICLES = 0b00010000
    ADMINISTRATOR = 0b11111111


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    summary = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    body_html = db.Column(db.Text)
    ta

    @staticmethod
    def generate_fake(count=50):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            #
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
        db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'abbr', 'acroym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre',
            'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
        # 注意正则表达式中的非贪婪匹配
        temp = re.sub('<.+?>', '', target.body_html)
        target.summary = re.sub('<.+', '', temp)[:200]
db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    disabled = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acroym', 'b', 'blockquote', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'), tags=allowed_tags, strip=True))
db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 头像的hash值，存储到数据库中可以避免重复计算浪费CPU性能
    portrait_hash = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 账户建立初始就根据Email判断管理员身份，
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='ADMINISTRATOR').first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.portrait_hash is None:
            self.portrait_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()

    def is_administrator(self):
        return self.can(Permissions.ADMINISTRATOR)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self, password):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def confirm_mod_email(self, token):
        # 修改Email的确认链接的响应函数
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        # 需要验证三种情况
        if data.get('confirm') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.portrait_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permission):
        return self.role is not None and self.role.permission & permission

    def gravatar(self, size=100, default='identicon', rating='g'):
        # is_secure继承自Werkzeug模块BaseRequest类
        # if request.is_secure:
        url = 'https://secure.gravatar.com/avatar'
        # else:
        # url = 'http://www.gravatar.com/avatar'
        hash_p = self.portrait_hash or hashlib.md5(self.email.encode('utf8')).hexdigest()
        return '{url}/{hash_p}?s={size}&d={default}&r={rating}'.format(
            url=url, hash_p=hash_p, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=50):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        # 初始化随机数生成器，以当前时间为参数
        seed()
        for i in range(count):
            u = User(
                email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                name=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            # 如果信息有重复，抛出异常
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permissions.COMMENT |
                     Permissions.FOLLOW |
                     Permissions.WRITE_ARTICLES, True),
            'Moderator': (Permissions.FOLLOW |
                          Permissions.COMMENT |
                          Permissions.WRITE_ARTICLES |
                          Permissions.MOD_ARTICLES |
                          Permissions.MOD_COMMENTS, False),
            'Administrator': (Permissions.ADMINISTRATOR, False)
        }
        for role in roles:
            r = Role.query.filter_by(name=role).first()
            if r is None:
                r = Role(name=role)
                r.default = roles[role][1]
                r.permission = roles[role][0]
            db.session.add(r)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
