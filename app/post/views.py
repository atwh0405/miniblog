#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import post
from .forms import PostForm
from ..user.forms import CommentForm
from ..models import Post, Permissions, Comment, User
from flask_login import current_user, login_required
from app import db
from flask import redirect, render_template, url_for, abort, flash
from instance.config import Config


@post.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            body=form.body.data,
            title=form.title.data,
            # 获取current_user代理的当前对象
            author=current_user._get_current_object())
        db.session.add(new_post)
        # 需要立即commit以生成id，因为后面用到主键id
        db.session.commit()
        flash(u'文章创建成功')
        return redirect(url_for('post.post_profile', id=new_post.id))
    return render_template('post/create_post.html', form=form)


@post.route('/<id>', methods=['POST', 'GET'])
def post_profile(id):
    post_c = Post.query.get_or_404(id)
    comments = post_c.comments.order_by(Comment.timestamp.desc()).all()
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.can(Permissions.COMMENT):
            comment = Comment(body=form.body.data,
                              author=current_user._get_current_object(),
                              post=post_c)
            db.session.add(comment)
            db.session.commit()
            flash(u'评论已发表')
            return redirect(url_for('post.post_profile', id=post_c.id))
        else:
            flash(u'请登陆后发表评论')
    return render_template('post/post_profile.html', post=post_c, form=form, comments=comments)


@post.route('/edit_post/<id>', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    post_c = Post.query.get_or_404(id)
    # 注意判断用户及权限
    if current_user != post_c.author and not current_user.can(Permissions.MOD_ARTICLES):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post_c.title = form.title.data
        post_c.body = form.body.data
        db.session.add(post_c)
        flash(u'文章已更新')
        return redirect(url_for('post.post_profile', id=post_c.id))
    form.title.data = post_c.title
    form.body.data = post_c.body
    return render_template('post/edit_post.html', form=form, post=post_c)


@post.route('/archive')
def archive():
    admin = User.query.filter_by(email=Config.ADMIN).first()
    posts = admin.posts
    return render_template('comp/archive_posts.html', posts=posts)
