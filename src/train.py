from SudokuNet import SudokuNet
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.datasets import mnist
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import classification_report
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to save model after training")
args = vars(ap.parse_args())

LEARNING_RATE = 1E-3
EPOCHS = 10
BATCH_SIZE = 128

(X_train, y_train), (X_test, y_test) = mnist.load_data()

X_train = X_train.reshape((X_train.shape[0], 28, 28, 1))
X_test = X_test.reshape((X_test.shape[0], 28, 28, 1))

X_train = X_train.astype("float32") / 255.0
X_test = X_test.astype("float32") / 255.0

# convert the labels from integers to vectors
le = LabelBinarizer()
y_train = le.fit_transform(y_train)
y_test = le.transform(y_test)

print("[INFO] compiling model...")
opt = Adam(lr=LEARNING_RATE)

model = SudokuNet.build(width=28, height=28, depth=1, classes=10)
model.compile(loss="categorical_crossentropy", 
    optimizer=opt,
	metrics=["accuracy"]
    )

print("[INFO] training network...")
history = model.fit(
	X_train, y_train,
	validation_data=(X_test, y_test),
	batch_size=BATCH_SIZE,
	epochs=EPOCHS,
	verbose=1)

print("[INFO] evaluating network...")
predictions = model.predict(X_test)
cr = classification_report(
    y_test.argmax(axis=1),
    predictions.argmax(axis=1),
    target_names=[str(x) for x in le.classes_]
)

print(cr)

# serialize the model to disk
print("[INFO] serializing digit model...")
model.save(args["model"], save_format="h5")