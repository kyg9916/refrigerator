# routes/refrigerator.py
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.extensions import db
from app.models import Ingredient
from datetime import datetime, date, timedelta
from sqlalchemy import extract, func  # ✨ DB 가공을 위한 함수 추가

bp = Blueprint('refrigerator', __name__)


@bp.route('/')
def index():
    today = date.today()
    three_days_later = today + timedelta(days=3)

    # 이번 달 가계부 계산을 위한 올해/이번달 추출
    current_year = today.year
    current_month = today.month

    search_query = request.args.get('search', '')
    page_expired = request.args.get('page_expired', 1, type=int)
    page_imminent = request.args.get('page_imminent', 1, type=int)
    page_fresh = request.args.get('page_fresh', 1, type=int)
    sort_fresh = request.args.get('sort_fresh', 'expiry_asc')
    per_page = 10

    # 📊 1. 가계부 통계용 계산 개선 (이번 달 지출액 기준)
    # 냉장고에 아직 남아있거나(is_consumed=False), 이번 달에 소비한(is_consumed=True 이고 소비월이 이번달인) 항목 대상
    stats_query = Ingredient.query.filter(
        (Ingredient.is_consumed == False) |
        ((Ingredient.is_consumed == True) &
         (extract('year', Ingredient.consumed_at) == current_year) &
         (extract('month', Ingredient.consumed_at) == current_month))
    )

    all_ingredients_for_stats = stats_query.all()
    total_spent = sum(item.price for item in all_ingredients_for_stats)

    # 🍎 카테고리별 이번 달 지출액 계산
    refrigerated_spent = sum(item.price for item in all_ingredients_for_stats if item.category == '냉장')
    frozen_spent = sum(item.price for item in all_ingredients_for_stats if item.category == '냉동')
    room_spent = sum(item.price for item in all_ingredients_for_stats if item.category == '실온')

    # 🔍 2. 냉장고 리스트용 베이스 쿼리 (현재 냉장고 안의 식재료만)
    query = Ingredient.query.filter_by(is_consumed=False)

    if search_query:
        query = query.filter(Ingredient.name.like(f"%{search_query}%"))

    expired_pagination = query.filter(Ingredient.expiry_date < today) \
        .order_by(Ingredient.expiry_date.asc()) \
        .paginate(page=page_expired, per_page=per_page, error_out=False)

    imminent_pagination = query.filter(Ingredient.expiry_date >= today, Ingredient.expiry_date <= three_days_later) \
        .order_by(Ingredient.expiry_date.asc()) \
        .paginate(page=page_imminent, per_page=per_page, error_out=False)

    # 🎯 3. 안전한 식재료 베이스 쿼리 분리
    fresh_query = query.filter(Ingredient.expiry_date > three_days_later)

    if sort_fresh == 'expiry_desc':
        fresh_query = fresh_query.order_by(Ingredient.expiry_date.desc())
    elif sort_fresh == 'price_asc':
        fresh_query = fresh_query.order_by(Ingredient.price.asc())
    elif sort_fresh == 'price_desc':
        fresh_query = fresh_query.order_by(Ingredient.price.desc())
    elif sort_fresh == 'category':
        fresh_query = fresh_query.order_by(Ingredient.category.asc(), Ingredient.expiry_date.asc())
    else:
        fresh_query = fresh_query.order_by(Ingredient.expiry_date.asc())

    fresh_pagination = fresh_query.paginate(page=page_fresh, per_page=per_page, error_out=False)

    # JSON 복사용 전체 활성 식재료 추출
    active_ingredients = Ingredient.query.filter_by(is_consumed=False).all()

    return render_template('index.html',
                           expired_items=expired_pagination.items,
                           expired_pagination=expired_pagination,
                           imminent_items=imminent_pagination.items,
                           imminent_pagination=imminent_pagination,
                           fresh_items=fresh_pagination.items,
                           fresh_pagination=fresh_pagination,
                           all_ingredients=active_ingredients,  # 💡 전체 캘린더/JSON용은 미소비 품목만 전달하여 깔끔하게 유지
                           search_query=search_query,
                           total_spent=total_spent,
                           sort_fresh=sort_fresh,
                           stats={
                               '냉장': refrigerated_spent,
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


# 🛠️ 소비 처리 시 시간 저장되도록 수정
@bp.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    item = Ingredient.query.get_or_404(item_id)
    if item:
        item.is_consumed = True
        item.consumed_at = datetime.utcnow()  # ✨ 중요: 소비한 현재 시간 기록
        db.session.commit()
    return redirect(url_for('refrigerator.index'))


# 🔄 이번달 가계부 지출 초기화 로직 수정
@bp.route('/reset-expense', methods=['POST'])
def reset_expense():
    try:
        today = date.today()
        # 데이터의 가격을 0으로 날리는 대신, 이번 달에 소비된 내역들의 소비 시간을 한 달 전으로 밀어서
        # 자연스럽게 '이번 달 통계'에서 빠지고 '이전 달 히스토리'로 축적되도록 만듭니다.
        consumed_this_month = Ingredient.query.filter(
            Ingredient.is_consumed == True,
            extract('year', Ingredient.consumed_at) == today.year,
            extract('month', Ingredient.consumed_at) == today.month
        ).all()

        for item in consumed_this_month:
            # 전달 말일로 변경하여 이번 달 통계에서 제외
            item.consumed_at = datetime(today.year, today.month, 1) - timedelta(days=1)

        db.session.commit()
        flash("이번 달 가계부 지출 금액이 성공적으로 초기화(이전 달로 백업)되었습니다.", "success")
    except Exception as e:
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
    return jsonify(events)  # calendar_events의 리턴문


# 밖으로 독립시킨 히스토리 뷰 함수
@bp.route('/history')
def history():
    # 소비 완료된 항목들을 최신 소비일 순으로 가져옴
    consumed_items = Ingredient.query.filter_by(is_consumed=True).order_by(Ingredient.consumed_at.desc()).all()

    # 월별로 데이터를 그룹화하기 위한 딕셔너리
    monthly_data = {}
    for item in consumed_items:
        if item.consumed_at:
            month_key = item.consumed_at.strftime('%Y년 %m월')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(item)

    return render_template('history.html', monthly_data=monthly_data)

@bp.route('/revert/<int:item_id>', methods=['POST'])
def revert(item_id):
    item = Ingredient.query.get_or_404(item_id)
    if item:
        item.is_consumed = False
        item.consumed_at = None  # 소비 시간 초기화
        db.session.commit()
    return redirect(url_for('refrigerator.history'))

    return jsonify(events)