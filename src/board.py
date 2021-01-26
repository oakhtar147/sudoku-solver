from numpy.lib.function_base import extract
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2
import os

IMAGE_PATH = r".\input\puzzle.jpeg"
image = cv2.imread(IMAGE_PATH)


def find_puzzle(image, debug=False):
    # convert the image to grayscale and blur it slightly
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 3)

    thresh = cv2.adaptiveThreshold(blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2)

    # invert the pixels
    thresh = cv2.bitwise_not(thresh)

    if debug:
        cv2.imshow("Puzzle Thresh", thresh)
        cv2.waitKey(2000)
        cv2.destroyWindow("Puzzle Thresh")

    # find contours in the thresholded image and sort them by size in
    # descending order
    contours = cv2.findContours(
        thresh.copy(), 
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
        )
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # initialize a contour that corresponds to the puzzle outline
    puzzleContour = None
    # loop over the contours

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02*perimeter, True)

        if len(approx) == 4:
            puzzleContour = approx
            break

    if puzzleContour is None:
        raise Exception(("No puzzle found"))

    if debug:
        output = image.copy()
        cv2.drawContours(output, 
            [puzzleContour], 
            -1, 
            (0, 0, 255), 2
            )
        cv2.imshow("Puzzle Contours", output)
        cv2.waitKey(2000)
        cv2.destroyWindow("Puzzle Contours")  

    puzzle = four_point_transform(image, puzzleContour.reshape(4, 2))  
    warped = four_point_transform(gray, puzzleContour.reshape(4, 2))  

    if debug:
        cv2.imshow("Puzzle aligned", puzzle)    
        cv2.waitKey(2000)
        cv2.destroyWindow("Puzzle aligned")

    return (puzzle, warped)    

def extract_digit(cell, debug=False):
    thresh = cv2.threshold(cell,
        0,
        255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = clear_border(thresh)    

    if debug:
        cv2.imshow("Thresh Cell", thresh)
        cv2.waitKey(0)

    contours = cv2.findContours(thresh.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)    

    if len(contours) == 0:
        return 

    c = max(contours, key=cv2.contourArea)
    mask = np.zeros(thresh.shape, dtype='uint8')
    cv2.drawContours(mask,
        [c],
        -1,
        255,
        -1) 

    (height, width) = thresh.shape
    percent_filled = cv2.countNonZero(mask) / float(height * width)

    if percent_filled < 0.03:
        return

    digit = cv2.bitwise_and(thresh, thresh, mask=mask)

    if debug:
        cv2.imshow("Digit")
        cv2.waitKey(0)          

    return digit

# find_puzzle(image, debug=True)