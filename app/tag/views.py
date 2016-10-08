#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import tag
from ..models import Tag, Post, Permissions
from flask import render_template, jsonify, request, abort
from flask_login import current_user
from .. import db
import json


@tag.route('/')
def tag_list():
    tags = Tag.query.all()
    return render_template('tag/tag_list.html', tags=tags)


@tag.route('/<id>')
def some_tag(id):
    tag_c = Tag.query.get_or_404(id)
    posts = tag_c.posts.all()
    return render_template('tag/some_tag.html', tag=tag_c, posts=posts)


@tag.route('/add_tag')
def add_tag():
    data = json.loads(request.args.get('data'))
    new_tag_name = data['new']
    if new_tag_name:
        post_id = data['post_id']
        post_c = Post.query.get_or_404(post_id)
        if current_user != post_c.author and not current_user.can(Permissions.MOD_ARTICLES):
            abort(403)
        new_tag = Tag.query.filter_by(name=new_tag_name).first()
        if not new_tag:
            new_tag = Tag(name=new_tag_name)
            db.session.add(new_tag)
        if new_tag not in post_c.tags:
            post_c.tags.append(new_tag)
            db.session.add(post_c)
            new_tag.posts.append(post_c)
            db.session.add(new_tag)
            db.session.commit()
            return jsonify(result='新标签已保存！')
    else:
        return jsonify(result='标签不能为空！')


@tag.route('/delete_tag')
def delete_tag():
    data = json.loads(request.args.get('data'))
    delete_tag_name = data['delete']
    post_id = data['post_id']
    post_c = Post.query.get_or_404(post_id)
    if current_user != post_c.author and not current_user.can(Permissions.MOD_ARTICLES):
        abort(403)
    to_delete_tag = Tag.query.filter_by(name=delete_tag_name).first()
    to_delete_tag.posts.remove(post_c)
    post_c.tags.remove(to_delete_tag)
    db.session.add(to_delete_tag, post_c)
    db.session.commit()
    return jsonify(result='标签已删除！')