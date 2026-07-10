# 🍎 나만의 냉장고 (My Fridge Management System)

> **"유통기한 관리는 스마트하게, 지출 관리는 꼼꼼하게!"** > Flask와 SQLite를 기반으로 제작된 로컬 친화형 식재료 및 유통기한 관리 웹 애플리케이션입니다.  
> 낭비되는 식재료를 줄이고 월간 소비 흐름을 한눈에 파악할 수 있도록 캘린더와 통계 기능을 제공합니다.

---

## 📌 주요 기능 (Key Features)

### 1. 🥦 직관적인 식재료 상태 분류
* **이미 지난 식재료**: 유통기한이 지나 빠르게 처리가 필요한 식재료를 붉은색 테이블로 경고합니다.
* **유통기한 임박**: 유통기한이 3일 이하로 남은 식재료를 노란색 테이블로 모아 보여주어 우선 소비를 유도합니다.
* **안전한 식재료**: 유통기한이 넉넉히 남은 신선한 식재료 목록입니다.

### 2. 📝 간편한 등록 및 수정/소비 관리
* 식재료명, 가격, 카테고리(냉장/냉동/실온), 유통기한을 한 번에 등록합니다.
* 테이블에서 즉시 수정 모달(Modal) 창을 띄워 정보를 손쉽게 변경할 수 있습니다.
* 식재료의 상태에 따라 `먹었음! (소비 완료)` 또는 `버림/삭제` 처리를 분기하여 가계부에 유기적으로 반영합니다.

### 3. 📅 유통기한 캘린더 (FullCalendar 연동)
* 월별 달력 화면을 통해 어떤 식재료의 유통기한이 언제 마감되는지 시각적으로 한눈에 파악할 수 있습니다.
* 달력의 특정 날짜를 클릭하면 새 식재료 등록 폼의 유통기한 날짜가 자동으로 입력되어 편리합니다.

### 4. 📊 카테고리별 지출 비율 및 가계부 통계 (Chart.js 연동)
* 이번 달에 소비 완료된 항목들을 포함하여 **총 누적 지출액**을 실시간 쉼표(`,`) 포맷으로 보여줍니다.
* 냉장, 냉동, 실온 각 카테고리별로 지출 비중이 얼마나 되는지 도넛 그래프(Doughnut Chart)로 시각화합니다.
* 필요 시 `이번달 초기화` 버튼을 통해 당월 지출 내역을 깔끔하게 리셋할 수 있습니다.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
* **Language:** Python 3.x
* **Framework:** Flask
* **Database & ORM:** SQLite / SQLAlchemy

### Frontend
* **UI Framework:** Bootstrap 5.3
* **Libraries:** FullCalendar 6.1.8, Chart.js

---

## ⚙️ 실행 방법 (Installation & Setup)

로컬 컴퓨터에서 본 프로젝트를 실행하려면 아래 단계를 따르세요.

### 1. 저장소 클론 및 이동
```bash
git clone [https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPOSITORY-NAME.git](https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPOSITORY-NAME.git)
cd YOUR-REPOSITORY-NAME
