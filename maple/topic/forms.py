#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: forms.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-05-20 18:08:44 (CST)
# Last Update:星期日 2016-11-13 12:35:51 (CST)
#          By:
# Description:
# **************************************************************************
from flask_wtf import Form
from maple.forums.models import Board
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from flask_babelex import lazy_gettext as _


class TopicForm(Form):
    title = StringField(_('Title:'), [DataRequired(), Length(min=4, max=36)])
    content = TextAreaField(_('Content:'), [DataRequired(), Length(min=6)])
    category = SelectField(_('Category:'),choices=[(2,'本地生活--本地生活')],coerce=int)
    # tags = SelectField(_('Tags:'),choices=[(1,'本地生活--本地生活')],coerce=int)
    tags = SelectField(_('Tags:'),choices=[('test','test'),('test1','test1')],coerce=unicode)
    choice = SelectField(
        'choice', choices=[(1, 'Markdown'), (2, 'Default')], coerce=int)


class ReplyForm(Form):
    content = TextAreaField(_('Content:'), [DataRequired()])
