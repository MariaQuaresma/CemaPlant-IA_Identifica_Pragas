import os
import tensorflow as tf
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads", "dataset"))
TRAIN_PATH = os.path.join(DATASET_PATH, "train")
VAL_PATH = os.path.join(DATASET_PATH, "valid")

IMG_SIZE = 224
EPOCHS = 15

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

train_data = train_data.prefetch(tf.data.AUTOTUNE)
val_data = val_data.prefetch(tf.data.AUTOTUNE)

with open(os.path.join(BASE_DIR, "class_names.json"), "w") as f:
    json.dump(class_names, f)

data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
])

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

for layer in base_model.layers[:-20]:
    layer.trainable = False

model = tf.keras.Sequential([
    data_augmentation,
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
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

model.save(os.path.join(BASE_DIR, "modelo_doencas.h5"))