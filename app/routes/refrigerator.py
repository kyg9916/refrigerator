from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.extensions import db
from app.models import Ingredient
from datetime import datetime, date, timedelta

bp = Blueprint('refrigerator', __name__)


@bp.route('/')
def index():
    today = date.today()
    three_days_later = today + timedelta(days=3)

    search_query = request.args.get('search', '')

    # 🔢 각 테이블별 현재 페이지 번호 안전하게 받아오기 (기본값 1)
    page_expired = request.args.get('page_expired', 1, type=int)
    page_imminent = request.args.get('page_imminent', 1, type=int)
    page_fresh = request.args.get('page_fresh', 1, type=int)

    per_page = 10  # ✨ 10개 단위로 세팅

    # 📊 1. 가계부 통계용 계산 (소비 여부 무관 전체 누적액)
    all_ingredients = Ingredient.query.all()
    total_spent = sum(item.price for item in all_ingredients)

    # 🍎 카테고리별 누적 지출액 계산 (그래프용)
    refrigerated_spent = sum(item.price for item in all_ingredients if item.category == '냉장')
    frozen_spent = sum(item.price for item in all_ingredients if item.category == '냉동')
    room_spent = sum(item.price for item in all_ingredients if item.category == '실온')

    # 🔍 2. 냉장고 리스트용 베이스 쿼리 (아직 안 먹은 것만)
    query = Ingredient.query.filter_by(is_consumed=False)

    if search_query:
        query = query.filter(Ingredient.name.like(f"%{search_query}%"))

    # 🔢 각 조건별 페이징 쿼리 수행
    expired_pagination = query.filter(Ingredient.expiry_date < today) \
        .order_by(Ingredient.expiry_date.asc()) \
        .paginate(page=page_expired, per_page=per_page, error_out=False)

    imminent_pagination = query.filter(Ingredient.expiry_date >= today, Ingredient.expiry_date <= three_days_later) \
        .order_by(Ingredient.expiry_date.asc()) \
        .paginate(page=page_imminent, per_page=per_page, error_out=False)

    fresh_pagination = query.filter(Ingredient.expiry_date > three_days_later) \
        .order_by(Ingredient.expiry_date.asc()) \
        .paginate(page=page_fresh, per_page=per_page, error_out=False)

    return render_template('index.html',
                           expired_items=expired_pagination.items,  # 실제 테이블에 뿌릴 리스트 10개
                           expired_pagination=expired_pagination,  # HTML 매크로에 넘겨줄 페이징 정보 객체
                           imminent_items=imminent_pagination.items,
                           imminent_pagination=imminent_pagination,
                           fresh_items=fresh_pagination.items,
                           fresh_pagination=fresh_pagination,
                           all_ingredients=all_ingredients,
                           search_query=search_query,
                           total_spent=total_spent,
                           stats={
                               '냉장': refrigerated_spent,
                               'frozen': frozen_spent,
                               '냉동': frozen_spent,
                               '실온': room_spent
                           })


@bp.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    category = request.form.get('category')
    expiry_date_str = request.form.get('expiry_date')
    price_str = request.form.get('price', '0')

    if name and expiry_date_str:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        price = int(price_str) if price_str.isdigit() else 0

        new_item = Ingredient(name=name, category=category, expiry_date=expiry_date, price=price)
        db.session.add(new_item)
        db.session.commit()

    return redirect(url_for('refrigerator.index'))


# 🛠️ 3. 식재료 정보 수정(Modify) 라우트
@bp.route('/update/<int:item_id>', methods=['POST'])
def update(item_id):
    item = Ingredient.query.get_or_404(item_id)
    if item:
        item.name = request.form.get('name')
        item.category = request.form.get('category')
        item.price = int(request.form.get('price', '0'))

        expiry_date_str = request.form.get('expiry_date')
        if expiry_date_str:
            item.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

        db.session.commit()
    return redirect(url_for('refrigerator.index'))


@bp.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    item = Ingredient.query.get_or_404(item_id)
    if item:
        item.is_consumed = True
        db.session.commit()
    return redirect(url_for('refrigerator.index'))


# 🔄 4. 이번달 가계부 지출 초기화 라우트 추가
@bp.route('/reset-expense', methods=['POST'])
def reset_expense():
    try:
        # 가계부 통계를 유지하면서 현재 누적 지출액만 리셋하기 위해,
        # 이미 소비 완료(is_consumed=True)된 항목들을 가격 0원으로 업데이트하여 전체 누적 금액에서 제외합니다.
        # (현재 냉장고에 보관 중인 '안 먹은 식재료'는 그대로 보존됩니다.)
        consumed_items = Ingredient.query.filter_by(is_consumed=True).all()

        for item in consumed_items:
            item.price = 0  # 지출 금액을 0으로 세팅하여 초기화 효과

        db.session.commit()
        flash("이번 달 가계부 지출 금액이 성공적으로 초기화되었습니다.", "success")
    except Exception as e:
        print(f"초기화 에러: {e}")
        db.session.rollback()
        flash("초기화 중 오류가 발생했습니다.", "danger")

    return redirect(url_for('refrigerator.index'))


@bp.route('/api/calendar-events')
def calendar_events():
    ingredients = Ingredient.query.filter_by(is_consumed=False).all()
    events = []

    for item in ingredients:
        event_title = f"[{item.category}] {item.name}"
        if item.price > 0:
            event_title += f" ({item.price:,}원)"

        events.append({
            'id': item.id,
            'title': event_title,
            'start': item.expiry_date.isoformat(),
            'color': '#3788d8' if item.category == '냉장' else ('#dc3545' if item.category == '냉동' else '#ffc107'),
            'textColor': '#ffffff' if item.category != '실온' else '#000000'
        })

    return jsonify(events)