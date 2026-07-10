from app.extensions import db
from datetime import datetime


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 식재료명
    category = db.Column(db.String(20), default='냉장')  # 냉장/냉동/실온
    expiry_date = db.Column(db.Date, nullable=False)  # 유통기한
    price = db.Column(db.Integer, default=0) # 가격
    is_consumed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)