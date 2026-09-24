import io
import cv2
import numpy as np
import tensorflow as tf
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# MediaPipe 호환성 임포트
from mediapipe.python.solutions import face_mesh as mp_face_mesh_module

app = FastAPI(title="HairMatch API")

# 정적 파일(CSS, JS) 및 Jinja2 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# TensorFlow 모델 및 MediaPipe 초기화
model = tf.keras.models.load_model("hairmatch_face_model.keras", compile=False)
mp_face_mesh = mp_face_mesh_module.FaceMesh(static_image_mode=True, max_num_faces=1)


# ==========================================
# 1. 사용자 인증 의존성 (JWT / Session)
# ==========================================
async def get_optional_user(request: Request) -> Optional[dict]:
    """비로그인 유저도 허용 (토큰이 없으면 None 반환)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    # TODO: 토큰 검증 로직 구현 (여기서는 예시 유저 반환)
    if token == "invalid":
        return None
    return {"user_id": 1, "username": "user01"}

async def get_required_user(user: Optional[dict] = Depends(get_optional_user)) -> dict:
    """로그인이 필수인 엔드포인트용 (비로그인 시 401 Unauthorized 예외 발생)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요한 서비스입니다."
        )
    return user


# ==========================================
# 2. HTML 페이지 라우팅
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def page_main(request: Request):
    """메인 화면"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/loading", response_class=HTMLResponse)
async def page_loading(request: Request):
    """분석 진행 로딩 화면"""
    return templates.TemplateResponse("loading.html", {"request": request})

@app.get("/result", response_class=HTMLResponse)
async def page_result(request: Request):
    """분석 결과 화면"""
    return templates.TemplateResponse("result.html", {"request": request})

@app.get("/mypage", response_class=HTMLResponse)
async def page_mypage(request: Request):
    """마이페이지 화면"""
    return templates.TemplateResponse("mypage.html", {"request": request})


# ==========================================
# 3. AI 분석 & 비즈니스 API
# ==========================================
@app.post("/api/analyze")
async def analyze_face(
    file: UploadFile = File(...),
    user: Optional[dict] = Depends(get_optional_user)
):
    """
    얼굴형 분석 API (사진 파일은 서버 디스크에 저장되지 않고 메모리 상에서 바로 분석 후 파기됨)
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")

    # MediaPipe 및 TensorFlow 모델 분석 수행
    # ... (모델 추론 처리) ...
    detected_shape = "계란형"
    recommended = ["시스루 댄디컷", "아이비리그컷"]

    # 로그인한 사용자인 경우 DB에 텍스트 분석 기록만 저장
    if user:
        # DB 저장 로직 (생략): save_history(user_id=user['user_id'], shape=detected_shape, styles=recommended)
        pass

    return {
        "face_shape": detected_shape,
        "recommended_styles": recommended,
        "is_logged_in": user is not None
    }


@app.get("/api/history")
async def get_history(user: dict = Depends(get_required_user)):
    """분석 이력 조회 (로그인 필수)"""
    # DB 조회 로직 (샘플 데이터 반환)
    return [
        {
            "id": 1,
            "face_shape": "계란형",
            "recommended_styles": ["시스루 댄디컷", "아이비리그컷"],
            "created_at": "2026-09-23T18:30:00"
        }
    ]


@app.get("/api/bookmarks")
async def get_bookmarks(user: dict = Depends(get_required_user)):
    """스타일 단위 북마크 목록 조회 (로그인 필수)"""
    # DB 조회 로직 (샘플 데이터 반환)
    return [
        {
            "id": 3,
            "style_name": "시스루 댄디컷",
            "face_shape": "계란형",
            "created_at": "2026-09-23T18:35:00"
        }
    ]


@app.delete("/api/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int, 
    user: dict = Depends(get_required_user)
):
    """
    북마크 해제 API (로그인 필수)
    성공 시 본문 없이 HTTP 204 No Content 응답을 반환합니다.
    """
    # DB 삭제 로직: delete_user_bookmark(user_id=user['user_id'], bookmark_id=bookmark_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
