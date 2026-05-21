import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_cors import CORS

load_dotenv()  # loads .env 可通过 os.environ访问

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app, supports_credentials=True)
    app.config.from_object('app.config.Config')

    # ensure folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROJECT_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.file_routes import file_bp
    from app.routes.project_routes import project_bp
    from app.routes.result_routes import result_bp
    from app.routes.edit_routes import edit_bp
    from app.routes.reuse_routes import reuse_bp
    from app.routes.reuse_first_stage_routes import reuse_first_stage_bp
    from app.routes.reuse_second_stage_route import reuse_second_stage_bp
    from app.routes.reuse_graph_routes import reuse_graph_bp
    from app.routes.reuse_upload_file_routes import reuse_upload_bp
    from app.routes.reuse_first_stage_edit_routes import reuse_first_stage_edit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(edit_bp)
    app.register_blueprint(reuse_bp)
    app.register_blueprint(reuse_first_stage_bp)
    app.register_blueprint(reuse_second_stage_bp)
    app.register_blueprint(reuse_graph_bp)
    app.register_blueprint(reuse_upload_bp)
    app.register_blueprint(reuse_first_stage_edit_bp)

    # index route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    return app
