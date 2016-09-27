#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import auth
from flask import flash, render_template, redirect, request, url_for, current_app, session
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
from .forms import LoginForm, RegistrationForm, Ch_passwordForm, Mod_Email
from ..models import User
from .. import db, login_manager
from ..email import send_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me)
            flash(u'登录成功')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码错误')
    return render_template('auth/login.html', form=form)

login_manager.login_message = u'请先登录'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'已登出')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '请确认您的邮件', 'auth/confirm_email', user=user, token=token)
        flash(u'一封确认邮件已发送到您的邮箱中，请确认其中的链接。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


# 请求钩子，在全局每次请求前执行
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        # 更新本次请求的发生时间
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/resend_confirm')
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '请确认您的邮件', 'auth/confirm_email', user=current_user, token=token)
    flash(u'一封确认邮件已发送到您的邮箱中，请确认其中的链接。')
    return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect('main.index')
    if current_user.confirm(token):
        flash(u'已确认成功！')
    else:
        flash(u'确认链接已过期，请重新发送确认邮件')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/ch_password', methods=['POST', 'GET'])
@login_required
def mod_password():
    form = Ch_passwordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        flash(u'密码已成功修改，请重新登录')
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('auth/ch_password.html', form=form)


@auth.route('/ch_email', methods=['POST', 'GET'])
@login_required
def mod_email():
    form = Mod_Email()
    if form.validate_on_submit():
        # 修改Email需对密码进行校验
        if not current_user.verify_password(form.password.data):
            if form.validate_on_submit():
                s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
                token = s.dumps({'confirm': current_user.id, 'email': form.new_email.data})
                send_email(
                    form.new_email.data, u'请确认您的新Email地址', 'auth/mod_email_emailbody', user=current_user, token=token)
                return render_template('auth/after_mod_email.html')
        else:
            flash(u'密码错误')
    return render_template('auth/mod_email.html', form=form)


@auth.route('/confirm_mod_email/<token>')
@login_required
def confirm_mod_email(token):
    if current_user.confirm_mod_email(token):
        flash(u'已确认成功！')
    else:
        flash(u'确认链接失效，请重新修改Email地址')
    return redirect(url_for('main.index'))


@auth.route('/resend_ch_email')
@login_required
def resend_confirm_mod_email():
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
    token = s.dumps({'confirm': current_user.id, 'email': session['NewEmail']})
    send_email(session['NewEmail'], '请确认您的新Email地址', 'auth/mod_email_emailbody', user=current_user, token=token)
    flash(u'一封确认邮件已发送')
    return render_template('auth/after_mod_email.html')