#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import flash, render_template, request, current_app
from . import main
from flask_login import login_required
from ..models import Permissions, Post


@main.app_context_processor
def inject_permissions():
    return dict(Permissions=Permissions)


@main.route('/')
def index():
    page = request.args.get('p', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('main/index.html', posts=posts, pagination=pagination)


@main.route('/about')
def about_me():
    return render_template('main/about_me.html')



