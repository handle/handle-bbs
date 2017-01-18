#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: filter.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-06-15 00:39:29 (CST)
# Last Update:星期六 2016-11-12 21:44:8 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime
import time

from flask_login import current_user
from maple.settings import setting
from maple.topic.models import Reply, Topic
from maple.user.models import User
from flask import Markup, g
from misaka import Markdown, HtmlRenderer
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from bleach import clean
from maple.extension import redis_data, cache
import pytz


def safe_clean(text):
    tags = ['b', 'i', 'font', 'br', 'blockquote', 'div', 'h2', 'a']
    attrs = {'*': ['style', 'id', 'class'], 'font': ['color'], 'a': ['href']}
    styles = ['color']
    return Markup(clean(text, tags=tags, attributes=attrs, styles=styles))

class Filters(object):

    def show_time(self):
        from flask_babelex import format_datetime
        if g.user.is_authenticated:
            return 'LOCALE:' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        else:
            return 'UTC:' + format_datetime(datetime.now(pytz.timezone('Asia/Shanghai')))

    def notice_count(self):
        from maple.forums.models import Notice
        if current_user.is_authenticated:
            count = Notice.query.filter_by(
                rece_id=g.user.id, is_read=False).count()
            if count > 0:
                return count
        return None

    @cache.memoize(timeout=60)
    def hot_tags(self):
        from maple.tag.models import Tags
        tags = Tags.query.order_by(Tags.time.desc()).limit(9).all()
        return tags

    @cache.memoize(timeout=60)
    def recent_tags(self):
        from maple.tag.models import Tags
        tags = Tags.query.order_by(Tags.time.desc()).limit(12).all()
        return tags


    class Title(object):
        title = setting['title']
        picture = setting['picture']
        description = setting['description']

    @staticmethod
    def get_user_infor(name):
        user = User.query.filter(User.username == name).first()
        return user

    @staticmethod
    def is_online(username):
        from maple.main.records import load_online_sign_users
        online_users = load_online_sign_users()
        if username in online_users:
            return True
        return False

    @staticmethod
    @cache.memoize(timeout=30)
    def is_collected(topicId):
        from maple.topic.models import CollectTopic
        from flask_login import current_user
        for collect in current_user.collects:
            cid = CollectTopic.query.filter_by(
                collect_id=collect.id, topic_id=topicId).first()
            if cid is not None:
                return True
        return False

    @staticmethod
    def safe_markdown(text):
        class HighlighterRenderer(HtmlRenderer):
            def blockcode(self, text, lang):
                lang = 'python'
                if not lang:
                    return '\n<pre><code>{}</code></pre>\n'.format(text.strip(
                    ))
                lexer = get_lexer_by_name(lang, stripall=True)
                formatter = HtmlFormatter()
                return highlight(text, lexer, formatter)

        renderer = HighlighterRenderer()
        md = Markdown(renderer, extensions=('fenced-code', ))
        return Markup(md(safe_clean(text)))

    @staticmethod
    def timesince(dt, default="just now"):
        from flask_babelex import format_datetime
        now = datetime.utcnow()
        diff = now - dt
        if diff.days > 10:
            return format_datetime(dt, 'Y-M-d H:m')
        elif diff.days <= 10 and diff.days > 0:
            periods = ((diff.days, "day", "days"), )
        elif diff.days <= 0 and diff.seconds > 3600:
            periods = ((diff.seconds / 3600, "hour", "hours"), )
        elif diff.seconds <= 3600 and diff.seconds > 90:
            periods = ((diff.seconds / 60, "minute", "minutes"), )
        else:
            return default

        for period, singular, plural in periods:

            if period:
                return "%d %s ago" % (period, singular
                                      if period == 1 else plural)

        return default

    @staticmethod
    @cache.memoize(timeout=30)
    def get_read_count(id):
        read = redis_data.hget('topic:%s' % str(id), 'read')
        replies = redis_data.hget('topic:%s' % str(id), 'replies')
        if not read:
            read = 0
        else:
            read = int(read)
        if not replies:
            replies = 0
        else:
            replies = int(replies)
        return replies, read

    @staticmethod
    @cache.memoize(timeout=60)
    def get_last_reply(uid):
        reply = Reply.query.join(Reply.topic).filter(Topic.id == uid).first()
        return reply

def register_jinja2(app):
    app.jinja_env.globals['Filters'] = Filters
    app.jinja_env.globals['Title'] = Filters.Title
    app.jinja_env.globals['hot_tags'] = Filters.hot_tags
    app.jinja_env.globals['recent_tags'] = Filters.recent_tags
    app.jinja_env.globals['notice_count'] = Filters.notice_count
    app.jinja_env.globals['show_time'] = Filters.show_time
    app.jinja_env.filters['get_last_reply'] = Filters.get_last_reply
    app.jinja_env.filters['get_user_infor'] = Filters.get_user_infor
    app.jinja_env.filters['get_read_count'] = Filters.get_read_count
    app.jinja_env.filters['timesince'] = Filters.timesince
    app.jinja_env.filters['markdown'] = Filters.safe_markdown
    app.jinja_env.filters['safe_clean'] = safe_clean
    app.jinja_env.filters['is_collected'] = Filters.is_collected
    app.jinja_env.filters['is_online'] = Filters.is_online
