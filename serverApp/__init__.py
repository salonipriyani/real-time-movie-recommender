# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
# from serverApp.populate import populate_user_ratings
import click
from flask import Flask, render_template
from serverApp.blueprints.recommend import recommend_bp
from serverApp.settings import config
# from serverApp.models import User
import pandas as pd
import logging

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('serverApp')
    
    app.config.from_object(config[config_name])
    app.logger.setLevel(logging.INFO)

    
    register_blueprints(app)
    


    return app


def register_blueprints(app):
    app.register_blueprint(recommend_bp)


