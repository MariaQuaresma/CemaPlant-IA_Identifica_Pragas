import os
import tensorflow as tf
import json

IMG_SIZE = 224
EPOCHS = 1
MAX_TRAIN_BATCHES = 200
MAX_VAL_BATCHES = 50

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads", "dataset"))
TRAIN_PATH = os.path.join(DATASET_PATH, "train")
VAL_PATH = os.path.join(DATASET_PATH, "valid")

if not os.path.isdir(TRAIN_PATH):
    raise FileNotFoundError(f"Pasta de treino nao encontrada: {TRAIN_PATH}")

if not os.path.isdir(VAL_PATH):
    raise FileNotFoundError(f"Pasta de validacao nao encontrada: {VAL_PATH}")

train_data = tf.keras.preprocessing.image_dataset_from_directory(
    TRAIN_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32
)

val_data = tf.keras.preprocessing.image_dataset_from_directory(
    VAL_PATH,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32
)

class_names = train_data.class_names

train_data = train_data.take(MAX_TRAIN_BATCHES).prefetch(tf.data.AUTOTUNE)
val_data = val_data.take(MAX_VAL_BATCHES).prefetch(tf.data.AUTOTUNE)

SAVE_DIR = os.path.join(BASE_DIR)

os.makedirs(SAVE_DIR, exist_ok=True)

with open(os.path.join(SAVE_DIR, "class_names.json"), "w") as f:
    json.dump(class_names, f)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("Iniciando treino...")
model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS
)
print("Treino finalizado!")

model.save(os.path.join(SAVE_DIR, "modelo_doencas.h5"))