#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
from flask import url_for, current_app, render_template, redirect, flash, request
from flask_login import login_required, current_user
from ..models import User, Post, Comment, Permissions
from ..decorators import permission_required
from .. import db
from ..models import User, Post


@admin.route('/')
@login_required
@permission_required(Permissions.ADMINISTRATOR)
def posts():
    page = request.args.get('p', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('admin/admin_index.html', posts=posts, pagination=pagination)


@admin.route('/users')
@login_required
@permission_required(Permissions.ADMINISTRATOR)
def users():
    users = User.query.order_by(User.since.desc()).all()
    return render_template('admin/users.html')


@admin.route('/delete_user/<id>')
@login_required
@permission_required(Permissions.ADMINISTRATOR)
def delete_user(d):
    pass


@admin.route('/delete_post/<id>')
@login_required
@permission_required(Permissions.ADMINISTRATOR)
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash(u'文章不存在！')
    else:
        db.session.delete(post)
        flash(u'文章已删除')
    return redirect(url_for('admin.posts'))


@admin.route('/comments')
@login_required
@permission_required(Permissions.ADMINISTRATOR)
def comments():
    pass


@admin.route('/delete_comment/<id>')
@login_required
@permission_required('ADMINISTRATOR')
def delete_comment():
    pass


@admin.route('/role_manage')
@login_required
@permission_required('ADMINISTRATOR')
def role_manage():
    pass
'''

from flask_admin.base import MenuLink
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView


class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_administrator()


class UnauthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_administrator()


class UserView(ModelView):
    can_delete = False
    create_modal = True
    column_exclude_list = ['password_hash', 'portrait_hash']
    column_searchable_list = ['username', 'name']
    column_filters = ['role']
    form_excluded_columns = ['portrait_hash', 'posts', 'comments', 'password_hash']

    def is_accessible(self):
        return current_user.is_administrator()


class PostView(ModelView):
    create_modal = True
    edit_modal = True
    form_excluded_columns = ['summary', 'comments']

    def is_accessible(self):
        return current_user.is_administrator()


class CommentView(ModelView):
    column_filters = ['disabled']
    can_create = False
    column_exclude_list = ['post']

    def is_accessible(self):
        return current_user.is_administrator()


