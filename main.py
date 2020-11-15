import cv2
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.python.keras.backend import shape
from core.flat2grid import flat2grid
from core.pic2flat import pic2flat
from core.sepdigit import sepdigit
from nn.core import predict

img = cv2.imread("core/sct8.jpg")
flatImg = pic2flat(img).getFinal()
girdImg = flat2grid(flatImg).getFinal()

# digit = cv2.imread("core/digit.png", 0)
# for digit in sepdigit(digit).getFinal():
#     plt.imshow(digit, cmap="gray"), plt.show()
#     digit = digit.astype("float32") / 255
#     digit = np.expand_dims(digit, -1)
#     print(predict(digit))


for box in girdImg:
    # plt.imsave("digit.png", box[1], cmap="gray", format="png")
    digits = sepdigit(box[1]).getFinal()
    if len(digits) == 0:
        continue
    print(box[0], end=" ")
    for digit in digits:
        # plt.imshow(digit, cmap="gray"), plt.show()
        digit = digit.astype("float32") / 255
        digit = np.expand_dims(digit, -1)
        print(predict(digit) * 1000, end="")
    plt.imshow(box[1], cmap="gray"), plt.show()
    print()