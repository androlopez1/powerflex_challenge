# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys
import os
import psycopg2
import json

from flask import Flask, render_template

from sprocket_factory import commands, public, user
from sprocket_factory.public.models import Factory, Sprocket
from sprocket_factory.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    migrate,
)

from sprocket_factory.commands import HERE


def create_app(config_object="sprocket_factory.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    
    #Feed the db with json files
    with app.app_context(): 
        db.create_all()
        insert_factories_from_json(Factory)
        insert_sprockets_from_json(Sprocket)
        
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)


def insert_factories_from_json(model):
    data_path = os.path.join(HERE,'data')
    with open(data_path+"/seed_factory_data.json") as f:
        factory_data = json.load(f)
        for index, item in enumerate(factory_data['factories']):
            obj = model.query.filter_by(id=index).all()
            if len(obj)==0:
                factory = model(id=index, chart_data=json.dumps(item))
                db.session.add(factory)
        db.session.commit()
    return None


def insert_sprockets_from_json(model):
    data_path = os.path.join(HERE,'data')
    with open(data_path+"/seed_sprocket_types.json") as f:
        sprocket_data = json.load(f)
        for index, item in enumerate(sprocket_data['sprockets']):
            obj = model.query.filter_by(id=index).all()
            if len(obj)==0:
                sprocket = model(id=index, teeth= item['teeth'], pitch_diameter= item['pitch_diameter'], outside_diameter= item['outside_diameter'], pitch= item['pitch'])
                db.session.add(sprocket)
        db.session.commit()
    return None