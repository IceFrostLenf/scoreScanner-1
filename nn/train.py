import numpy as np
import imutils
import imgaug as ia
import imgaug.augmenters as iaa
from tensorflow.keras import Sequential, Input, layers
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical

num_classes = 10
input_shape = (28, 28, 1)
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x = np.concatenate((x_train, x_test)).astype("float32") / 255
y = np.concatenate((y_train, y_test))  # data augmentation


def shift_image(image, dx, dy):
    return imutils.translate(image, dx, dy)


print("Creating Augmented Dataset...")
x_augmented = [image for image in x]
y_augmented = [image for image in y]

offset = 5
rotate_deg = 45
shear_deg = 45
rotate = iaa.Affine(rotate=(-rotate_deg, rotate_deg))
gaussian_noise = iaa.AdditiveGaussianNoise(5, 5)
crop = iaa.Crop(percent=(0, 0.3))
shear = iaa.Affine(shear=(0, shear_deg))

for image, label in zip(x, y):
    for dx, dy in ((offset, 0), (-offset, 0), (0, offset), (0, -offset)):
        # shift
        shift = shift_image(image, dx, dy)
        x_augmented.append(shift)
        y_augmented.append(label)
    # rotate
    rotate_img = rotate.augment_image(image)
    x_augmented.append(rotate_img)
    y_augmented.append(label)
    # noise
    noise_img = gaussian_noise.augment_image(image)
    x_augmented.append(noise_img)
    y_augmented.append(label)
    # shear
    shear_img = shear.augment_image(image)
    x_augmented.append(shear_img)
    y_augmented.append(label)
    # crop
    crop_img = shear.augment_image(image)
    x_augmented.append(crop_img)
    y_augmented.append(label)

x_augmented = np.array(x_augmented)
y_augmented = np.array(y_augmented)

x = np.expand_dims(x_augmented, -1)
y = to_categorical(y_augmented, num_classes)

del x_augmented
del y_augmented
del x_train
del y_train
del x_test
del y_test

print(x.shape)
print(y.shape)

model = Sequential(
    [
        Input(shape=input_shape),
        Conv2D(500, kernel_size=(5, 5), activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(500, kernel_size=(3, 3), activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dropout(0.5),
        Dense(128, activation="relu"),
        Dense(256, activation="relu"),
        Dense(num_classes, activation="softmax"),
    ]
)

print(model.summary())
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(x, y, epochs=10, batch_size=128, verbose=1)
model.save("mnist_cnn.h5")