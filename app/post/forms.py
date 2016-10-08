#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    title = StringField('题目', validators=[DataRequired(), Length(1, 64)])
    body = PageDownField('在这里写点东西吧', validators=[DataRequired()])
    submit = SubmitField('提交')