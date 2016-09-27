#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import User, Role
from flask_pagedown.fields import PageDownField

import sys
reload(sys)
sys.setdefaultencoding('utf8')


class CommentForm(Form):
     body = PageDownField('写评论', validators=[DataRequired()])
     submit = SubmitField('提交')


class EditProfileForm(Form):
    name = StringField('昵称', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('关于你自己')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z0-9][A-Za-z0-9_.]*$', 0, '用户名包括字母、数字、点和下划线')])
    confirmed = BooleanField('账户已确认')
    role = SelectField('用户身份', coerce=int)
    name = StringField('昵称', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已被注册')

    def validat_username(self, field):
        if field.data != self.user.username and\
                User.query.filter_by(username=self.username.data).first():
            raise ValidationError('用户名已被注册')