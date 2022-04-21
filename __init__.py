from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():        
        # Create Flask application
        app = Flask(__name__)        
        # Create dummy secrey key so we can use sessions
        app.config['SECRET_KEY'] = '1234567890'        
        # Create in-memory database
        app.config['DATABASE_FILE'] = 'FE_DATABASE.sqlite'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
        # deactivate Flask-SQLAlchemy track modifications
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        #app.register_blueprint(admin , url_prefix='/admin')
        db.init_app(app) # Initialiaze sqlite database
        with app.app_context():
                 db.create_all()
        return app
