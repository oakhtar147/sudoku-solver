# import the necessary packages
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Activation,
    Flatten,
    Dense,
    Dropout
)

class SudokuNet:
    @staticmethod
    def build(width, height, depth, classes):
        model = Sequential()
        input_shape = (height, width, depth)

        model.add(
            Conv2D(input_shape=(height, width, depth),
                filters=32, 
                kernel_size=(3,3), 
                strides=(1,1),
                padding="same",
            )
        )

        model.add(
            MaxPooling2D(
                pool_size=(2,2), 
                strides=(1,1),
                padding="valid"
            )
        )

        model.add(Activation("relu"))

        model.add(
            Conv2D(
                filters=64, 
                kernel_size=(5,5), 
                strides=2,
                padding="same"
            )
        )

        model.add(
            MaxPooling2D(
                pool_size=(2,2), 
                strides=(1,1),
                padding="valid"
            )
        )

        model.add(Activation("relu"))


        model.add(Flatten())
        model.add(Dropout(0.5))
        model.add(
            Dense(classes)
        )

        model.add(Activation("softmax"))

        return model