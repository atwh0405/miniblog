#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import redirect, render_template
from flask_wtf import Form
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    title = StringField(u'题目', validators=[DataRequired(), Length(1, 64)])
    body = PageDownField(u'在这里写点东西吧', validators=[DataRequired()])
    submit = SubmitField(u'提交')
