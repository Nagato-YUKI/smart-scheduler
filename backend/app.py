from flask import Flask
from flask_cors import CORS
from config import Config
from peewee_manager import _database, Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    _database.init(Config.DATABASE)
    _database.connect()

    from routes import register_blueprints
    register_blueprints(app)

    @app.teardown_appcontext
    def close_db(exc):
        if not _database.is_closed():
            _database.close()

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
