#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: urls.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-07-15 19:23:48 (CST)
# Last Update:星期日 2016-11-13 12:26:30 (CST)
#          By:
# Description:
# **************************************************************************
from flask import Blueprint, abort, g
from maple.user.models import User
from .views import (UserView, TopicView, ReplyView, CollectView,
                    CollectListView, FollowerView, FollowingView)

site = Blueprint('user', __name__)


@site.url_value_preprocessor
def pull_user_url(endpoint, values):
    g.user_url = values.pop('user_url')
    user = User.query.filter_by(username=g.user_url).first()
    if user is None:
        abort(404)


@site.url_defaults
def add_user_url(endpoint, values):
    if 'user_url' in values or not g.user_url:
        return
    values['user_url'] = g.user_url


user_view = UserView.as_view('user')
topic_view = TopicView.as_view('topic')
reply_view = ReplyView.as_view('reply')
collectlist_view = CollectListView.as_view('collect')
collect_view = CollectView.as_view('collect_detail')
follower_view = FollowerView.as_view('follower')
following_view = FollowingView.as_view('following')

site.add_url_rule('', view_func=user_view)
site.add_url_rule('/topics', view_func=topic_view)
site.add_url_rule('/replies', view_func=reply_view)
site.add_url_rule('/collects', view_func=collectlist_view)
site.add_url_rule('/collects/<int:collectId>', view_func=collect_view)
site.add_url_rule('/following', view_func=following_view)
site.add_url_rule('/followers', view_func=follower_view)
