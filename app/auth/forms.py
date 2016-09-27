#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class LoginForm(Form):
    email = StringField('Email', validators=[Email(), Length(1, 64), DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('提交')


class Ch_passwordForm(Form):
    old_password = PasswordField('输入旧密码', validators=[DataRequired()])
    new_password = PasswordField('输入新密码', validators=[DataRequired()])
    new_password2 = PasswordField('再次输入新密码', validators=[
        DataRequired(), EqualTo('new_password', message='两次密码不一致')])
    submit = SubmitField('确认修改')


class Mod_Email(Form):
    new_email = StringField(u'新Email', validators=[Email(), Length(1, 64), DataRequired()])
    password = PasswordField(u'输入账号密码', validators=[DataRequired(), Length(64)])
    submit = SubmitField('确认修改')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z0-9][A-Za-z0-9_.]*$', 0, '用户名包括字母、数字、点和下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(),
        EqualTo('password2', message='两次密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该Email已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册')