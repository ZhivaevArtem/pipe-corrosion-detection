import os

from flask import Flask
from flask_mail import Mail

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'defapp.sqlite'),
)

# mail configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME='pigin.labdef@gmail.com',
    MAIL_PASSWORD='Defect101',
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True
)
mail=Mail()
mail.init_app(app)


import db
db.init_app(app)

import auth
app.register_blueprint(auth.bp)

import blog
app.register_blueprint(blog.bp)
app.add_url_rule('/', endpoint='index')