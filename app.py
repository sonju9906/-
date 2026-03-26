import tensorflow as tf
import numpy as np
from PIL import Image
import io
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

# 1. 모델 로드 (학교에서 만든 .h5 파일 이름으로 바꾸세요)
# 예: model = tf.keras.models.load_model('face_shape_model.h5')
try:
    model = tf.keras.models.load_model('my_model.h5')
    print("✅ AI 모델 로드 성공!")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")

@app.post("/analyze")
async def analyze_face(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB')
    
    # 2. 전처리 (모델 학습 시 설정했던 크기, 예: 224)
    img = img.resize((224, 224)) 
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # 3. 예측
    predictions = model.predict(img_array)
    result_idx = np.argmax(predictions[0])
    
    # 4. 라벨 (학교 프로젝트 기준에 맞게 수정)
    labels = ['Oval', 'Round', 'Square', 'Heart']
    return {"face_shape": labels[result_idx]}