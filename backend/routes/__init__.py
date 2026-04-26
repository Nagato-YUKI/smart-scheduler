from .rooms import rooms_bp
from .teachers import teachers_bp
from .classes import classes_bp
from .courses import courses_bp
from .holidays import holidays_bp
from .schedule import schedule_bp
from .import_data import import_bp

__all__ = ['rooms_bp', 'teachers_bp', 'classes_bp', 'courses_bp', 'holidays_bp', 'schedule_bp', 'import_bp']


def register_blueprints(app):
    app.register_blueprint(rooms_bp, url_prefix='/api')
    app.register_blueprint(teachers_bp, url_prefix='/api')
    app.register_blueprint(classes_bp, url_prefix='/api')
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(holidays_bp, url_prefix='/api')
    app.register_blueprint(schedule_bp, url_prefix='/api')
    app.register_blueprint(import_bp)
