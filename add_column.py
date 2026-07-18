import sqlite3
import os

# 1. 본인의 SQLite DB 파일 경로를 적어주세요.
# Flask 공식 가이드를 따랐다면 보통 instance 폴더 안에 있습니다.
db_path = 'instance/refrigerator.db'

# 만약 instance 폴더가 아니라 프로젝트 메인 폴더에 있다면 아래 경로로 변경됩니다.
if not os.path.exists(db_path):
    db_path = 'refrigerator.db'

try:
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. ingredients 테이블에 consumed_at 컬럼을 DATETIME 타입으로 추가 (기존 데이터는 자동으로 NULL 처리됨)
    cursor.execute("ALTER TABLE ingredients ADD COLUMN consumed_at DATETIME;")

    conn.commit()
    print("✅ 성공: ingredients 테이블에 consumed_at 컬럼이 안전하게 추가되었습니다!")
    print("이제 기존 데이터를 그대로 사용하실 수 있습니다.")

except sqlite3.OperationalError as e:
    print(f"❌ 오류 발생: {e}")
    print("DB 파일 경로가 맞는지 확인하시거나 이미 컬럼이 추가되었는지 확인해 주세요.")
finally:
    if 'conn' in locals():
        conn.close()