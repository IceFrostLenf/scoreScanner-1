from itertools import groupby
from matplotlib.pyplot import box, grid
import numpy as np
import cv2
from matplotlib import pyplot as plt
from skimage import measure


class flat2grid:
    def __init__(self, __img):
        self.img = __img
        self.__final = None
        self.__preprocess()
        self.__process()

    def getFinal(self):
        return self.__final

    def __preprocess(self):
        self.__bw_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.__shape = self.__bw_img.shape
        # cv2.rectangle(self.__bw_img, (0, 0), (800, 1000), (0, 0, 0), 3)
        binary = cv2.adaptiveThreshold(
            ~self.__bw_img,
            10,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            45,
            0,
        )
        rows, cols = self.__shape
        scale = 40
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_col = cv2.dilate(eroded, kernel, iterations=1)
        scale = 20
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_row = cv2.dilate(eroded, kernel, iterations=1)
        self.__outline = cv2.bitwise_or(dilated_col, dilated_row)
        self.__cross = cv2.bitwise_and(dilated_col, dilated_row)

    def __process(self):
        dots = [(5, 5)]
        labels, num = measure.label(
            self.__cross, connectivity=2, background=0, return_num=True
        )
        for i in range(1, num + 1):
            x, y = np.where(labels == i)
            dots.append(
                tuple(reversed(np.asarray(np.dstack((x, y))[0], dtype=int)[0].tolist()))
            )
        boxes = []

        def slope(x, y):
            dy = y[0] - x[0]
            dx = y[1] - x[1]
            return np.inf() if dx == 0 else dy / dx

        while len(dots) != 0:
            start = dots[0]
            end = sorted(
                list(
                    filter(
                        lambda x: (x[0] - start[0] > 0)
                        and (x[1] - start[1] > 0)
                        and (0.5 < slope(start, x) < 10),
                        dots,
                    )
                ),
                key=lambda x: np.linalg.norm(np.array([x]) - np.array([start])),
            )
            if len(end) != 0:
                end = end[0]
                boxes.append([start, end])
            elif (
                self.__shape[1] - 30 > start[0] > self.__shape[1] - 70
                and start[1] < self.__shape[0] - 20
            ):
                end = (start[0] + 60, start[1] + 28)
                boxes.append([start, end])
            dots.remove(start)
        for box in boxes:
            cv2.rectangle(
                self.img,
                (box[0][0], box[0][1]),
                (box[1][0], box[1][1]),
                (255, 255, 0),
                2,
            )
            crop = self.img[box[0][1] : box[1][1], box[0][0] : box[1][0]]
        plt.imshow(self.img), plt.show()