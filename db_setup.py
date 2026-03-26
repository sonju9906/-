import sqlite3

# 1. DB 연결 (파일이 없으면 자동으로 생성됩니다)
conn = sqlite3.connect('capstone_design.db')
cur = conn.cursor()

# 2. 추천 리스트를 담을 테이블 생성
# face_shape: 분석 결과값, style_name: 헤어 이름, advice: 연출 팁
cur.execute('''
CREATE TABLE IF NOT EXISTS hair_recommend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    face_shape TEXT NOT NULL,
    style_name TEXT NOT NULL,
    advice TEXT
)
''')

# 3. 팀에서 정한 추천 리스트 (데이터 매칭)
# (얼굴형 결과값, 추천 헤어스타일, 연출 팁)
recommend_list = [
    ('Oval Face (계란형)', '웨이브 단발', '앞머리를 내려 얼굴을 작고 갸름하게 연출'),
    ('Round Face (동그란형)', '보이시한 커트 단발', '최대한 길어 보이게 연출'),
    ('Square Face (각진형)', '앞머리 없는 롱헤어', '각진 부분을 부드럽게 커버'),
    ('Pointed Face (턱 도드라진형)', '롱헤어', '시선을 아래로 분산시켜 턱 라인 보완')
]

# 4. 데이터를 DB에 한꺼번에 밀어넣기
cur.executemany('INSERT INTO hair_recommend (face_shape, style_name, advice) VALUES (?, ?, ?)', recommend_list)

# 5. 변경사항 저장 및 연결 종료
conn.commit()
conn.close()

print("✅ 팀 추천 리스트가 DB에 성공적으로 저장되었습니다!")