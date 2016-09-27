#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import user
from flask import render_template, redirect, abort, flash, url_for, request, current_app
from flask_login import current_user
from ..models import User, Post, Comment
from .forms import EditProfileForm, EditProfileAdminForm
from flask_login import login_required
from app import db


@user.route('/<username>')
def user_profile(username):
    post_page = request.args.get('p', 1, type=int)
    user_c = User.query.filter_by(username=username).first()
    # Post中backref设置为lazy=dynamic，因此user.posts为query对象，需增加过滤器
    pagination = user_c.posts.order_by(Post.timestamp.desc()).paginate(
        post_page, per_page=current_app.config['PER_PAGE'], error_out=False)
    posts = pagination.items
    if user_c is None:
        abort(404)
    return render_template('user/user_profile.html', user=user_c,
                           posts=posts,
                           pagination=pagination)


@user.route('/<username>/comments')
def user_profile_comments(username):
    comment_page = request.args.get('cp', 1, type=int)
    user_c = User.query.filter_by(username=username).first()
    pagination = user_c.comments.order_by(Comment.timestamp.desc()).paginate(
        comment_page, per_page=current_app.config['PER_PAGE'], error_out=False)
    comments = pagination.items
    print pagination.pages
    print comments
    if user_c is None:
        abort(404)
    return render_template('user/user_profile.html', user=user_c,
                           comments=comments,
                           pagination=pagination)


@user.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人资料已更新')
        return redirect(url_for('user.user_profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html', form=form)


@user.route('/edit_profile/<int:id>', methods=['POST', 'GET'])
def edit_profile_by_admin(id):
    user_c = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user_c)
    if form.validate_on_submit():
        user_c.email = form.email.data
        user_c.username = form.username.data
        user_c.confirmed = form.confirmed.data
        user_c.role = form.role.data
        user_c.name = form.name.data
        user_c.location = form.location.data
        user_c.about_me = form.about_me.data
        db.session.add(user_c)
        return redirect(url_for('user.user_profile', username=user_c.username))
    form.email.data = user_c.email
    form.username.data = user_c.username
    form.confirmed.data = user_c.confirmed
    form.role.data = user_c.role
    form.name.data = user_c.name
    form.location.data = user_c.location
    form.about_me.data = user_c.about_me
    return render_template('user/edit_profile_by_admin.html', form=form, user=user_c)
