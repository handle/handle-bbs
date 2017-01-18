# !/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: run.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2016-02-07 09:12:47
# *************************************************************************
from flask import g
from flask_login import current_user
from maple import create_app
from maple.common.middleware import get_online
from maple.forums.forms import SearchForm, SortForm, MessageForm
from werkzeug.contrib.fixers import ProxyFix
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.before_request
def before():
    g.user = current_user
    g.search_form=SearchForm()
    g.get_online = get_online()
    g.sort_form = SortForm();
    g.message_form= MessageForm()

if __name__ == '__main__':
    app.run()
