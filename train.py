import tensorflow as tf
from tensorflow.keras import layers, models
import os

# 1. 데이터 설정
data_dir = 'dataset' # 사진이 들어있는 폴더
img_height, img_width = 224, 224
batch_size = 32

# 2. 이미지 데이터 불러오기
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

# 3. 간단한 AI 모델 설계 (CNN)
model = models.Sequential([
    layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(4, activation='softmax') # 결과 종류가 4개(달걀,둥근,각진,하트)
])

# 4. 학습 시작
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

model.fit(train_ds, validation_data=val_ds, epochs=10)

# 5. 모델 저장 (이게 있어야 웹에서 씁니다!)
model.save('face_model.h5')
print("✅ 모델 학습 완료 및 face_model.h5 저장 성공!")