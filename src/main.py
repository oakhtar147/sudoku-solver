from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

import solver
from board import (
    find_puzzle,
    extract_digit
)

import time
import numpy as np
import argparse
import imutils
import cv2
import itertools

MODEL = './model/digit_classifier'
IMAGE = './input/puzzle.jpeg'
DEBUG = True

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=False,
	help="path to trained digit classifier")
ap.add_argument("-i", "--image", required=False,
	help="path to input Sudoku puzzle image")
ap.add_argument("-d", "--debug", type=int, default=-1,
	help="whether or not we are visualizing each step of the pipeline")
args = vars(ap.parse_args())


def main(model, image, debug=False):
    """
    Params: 
        (str) model: path to model with .h5 extension
        (str) image: path to image
        (bool) debug: Set to true if you want the intermediate results (default is False)

        Displays the end result. Might also display the intermediate results if debug = True
    """

    model = load_model(model)

    image = cv2.imread(image)
    image = imutils.resize(image, width=600)


    puzzle, warped = find_puzzle(image, debug)
    board = np.zeros((9, 9), dtype="int")

    stepX = warped.shape[1] // 9
    stepY = warped.shape[0] // 9

    cell_locations = []

    for y in range(0, 9):
        row = []
        
        for x in range(0, 9):
            startX = x * stepX
            startY = y * stepY
            endX = (x + 1) * stepX
            endY = (y + 1) * stepY

            row.append((startX, startY, endX, endY))

            cell = warped[startY:endY, startX:endX]
            digit = extract_digit(cell, False)

            if digit is not None:
                roi = cv2.resize(digit, (28, 28)) # for the model
                roi = roi.astype("float") / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)

                prediction = model.predict(roi).argmax(axis=1)[0] # get the class with the max prob
                board[y, x] = prediction

        cell_locations.append(row)

    flattened_board = list(itertools.chain.from_iterable(board))
    flattened_board = [str(x) if x != 0 else '.' for x in flattened_board]
    board = "".join(flattened_board)

    # record the time for algorithm to solve the board, shown in the results window name
    start = time.time()

    # solving the puzzle
    values = solver.grid2values(board)
    result = solver.search(values)

    time_taken = time.time() - start

    row_results = np.array([val for val in result.values()]) \
        .reshape(9, 9) \
        .tolist()

    # putting the text on the image and then displaying it
    for (cellRow, boardRow) in zip(cell_locations, row_results):

        for (box, digit) in zip(cellRow, boardRow):
            startX, startY, endX, endY = box

            textX = int((endX - startX) * 0.33) 
            textY = int((endY - startY) * -0.2)
            textX += startX
            textY += endY

            cv2.putText(puzzle,
                str(digit), 
                (textX, textY),
                cv2.FONT_HERSHEY_COMPLEX, 
                0.8, (0, 0, 255), 2)

    cv2.imshow(f"Result, time taken {time_taken * 1000:.2f}ms", puzzle)
    cv2.waitKey(0)

if __name__ == "__main__":
    main(MODEL, IMAGE, DEBUG)    