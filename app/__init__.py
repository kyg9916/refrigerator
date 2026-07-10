from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__, template_folder='../templates') # 템플릿 경로 지정
    app.config.from_object(Config)

    # DB 초기화
    db.init_app(app)

    # Blueprint 등록
    from app.routes.refrigerator import bp as fridge_bp
    app.register_blueprint(fridge_bp)

    # DB 테이블 생성 (처음 한 번만 실행됨)
    with app.app_context():
        db.create_all()

    return app