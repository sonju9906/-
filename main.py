import cv2
import mediapipe as mp
import sqlite3
import os

# 1. DB에서 추천 정보 가져오는 함수
def get_recommendation(face_shape):
    try:
        # DB 연결
        conn = sqlite3.connect('capstone_design.db')
        cur = conn.cursor()
        
        # 얼굴형에 맞는 데이터 조회 (SQL 쿼리)
        query = "SELECT style_name, advice FROM hair_recommend WHERE face_shape = ?"
        cur.execute(query, (face_shape,))
        result = cur.fetchone()
        
        conn.close()
        return result # (스타일이름, 조언) 튜플 반환
    except sqlite3.Error as e:
        print(f"DB 에러: {e}")
        return None

# 2. 얼굴 분석 및 매칭 함수
def analyze_and_match(image_path):
    mp_face_mesh = mp.solutions.face_mesh
    image = cv2.imread(image_path)
    if image is None: return

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 1단계: 비율 계산 (이전과 동일)
                top, bottom = face_landmarks.landmark[10].y, face_landmarks.landmark[152].y
                left, right = face_landmarks.landmark[234].x, face_landmarks.landmark[454].x
                ratio = abs(bottom - top) / abs(right - left)

                # 얼굴형 결정
                if ratio > 1.5: res_shape = "Long Face (긴 얼굴형)" # 추가된 로직에 맞춰 이름 통일
                elif ratio > 1.3: res_shape = "Oval Face (계란형)"
                else: res_shape = "Round Face (동그란형)"

                # 2단계: DB 연동 (매칭)
                recommend = get_recommendation(res_shape)

                if recommend:
                    style, advice = recommend
                    print(f"\n✨ [분석 결과]: {res_shape}")
                    print(f"💇 [추천 헤어]: {style}")
                    print(f"💡 [전문가 조언]: {advice}")
                    
                    # 화면에 결과 텍스트 쓰기 (한글 깨짐 방지를 위해 영어로 표기하거나 출력만 확인)
                    cv2.putText(image, f"Shape: {res_shape}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(image, f"Style: {style}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
            cv2.imshow('Final Result', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("얼굴을 찾을 수 없습니다.")

# 실행 (본인의 이미지 파일명으로 변경)
analyze_and_match('my_face.jpg')