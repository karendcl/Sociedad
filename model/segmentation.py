# import opencv
import cv2
import sys, os, pathlib

import cv2
import numpy as np
from scipy.signal import savgol_filter

def preprocess_image(image_path):
    # Convert image to grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # apply gaussian filter
    image = cv2.GaussianBlur(image, (9, 9), 0)
    # apply median filter
    image = cv2.medianBlur(image, 5)
    # # Apply binary thresholding
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary_image



def smooth_hpp(hpp, window_length=51, polyorder=3):
    # Apply Savitzky-Golay filter for smoothing
    smoothed_hpp = savgol_filter(hpp, window_length, polyorder)
    return smoothed_hpp

def detect_line_boundaries(hpp, smoothed_hpp, threshold_fraction=0.2, padding=15):
    # Calculate dynamic threshold based on HPP average intensity
    threshold = np.max(smoothed_hpp) * threshold_fraction
    lines = []
    in_line = False
    for i, value in enumerate(smoothed_hpp):
        if value > threshold and not in_line:
            start = max(0, i - padding)
            in_line = True
        elif value < threshold and in_line:
            end = min(len(hpp)-1, i + padding)
            lines.append((start, end))
            in_line = False
    return lines

def draw_segmentation_lines(image, lines, name, BASE_DIR):
    orig_img = cv2.imread(name)

    os.chdir(os.path.join(BASE_DIR, "model", "temp"))

    names = []
    raw_names = []
    for i, (start, end) in enumerate(lines):
        crop_img = orig_img[start:end, :]
        cv2.imwrite(f'segm_{i}.jpg', crop_img)
        names.append(os.path.join(BASE_DIR, "model", "temp", f'segm_{i}.jpg'))
        raw_names.append(f'segm_{i}.jpg')

    os.chdir(BASE_DIR)
    return names, raw_names

def seg_image(image_path, BASE_DIR):
    # Load and preprocess the image
    binary_image = preprocess_image(image_path)

    # Calculate the horizontal projection profile
    hpp = np.sum(binary_image, axis=1)

    # Smooth the horizontal projection profile
    smoothed_hpp = smooth_hpp(hpp)

    # Detect line boundaries using the smoothed HPP
    line_boundaries = detect_line_boundaries(hpp, smoothed_hpp)

    # Draw segmentation lines on the original image
    segmented_image, raw_names = draw_segmentation_lines(binary_image, line_boundaries, image_path, BASE_DIR)

    return segmented_image, raw_names

def segmentation(img_path, BASE_DIR):
    img = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh2 = cv2.threshold(img_gray, 20, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)


    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 5))
    dilation = cv2.dilate(thresh2, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    im2 = img.copy()

    ING_LIST = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        ING_LIST.append((x, y, w, h))


    ING_LIST = [x for x in ING_LIST if x[2] > 15 and x[3] < 50]


    WIDTH = im2.shape[1]
    AVG_HEIGHT = sum([x[3] for x in ING_LIST]) / len(ING_LIST)
    print(AVG_HEIGHT)

    ING_LIST.sort(key=lambda x: x[1])

    last_y = None
    lines_del = []

    for x,y,w,h in ING_LIST:
        if last_y is None:
            last_y = y + h
            continue
        if y < last_y:
            if last_y - y < AVG_HEIGHT:
                lines_del.append((x,y,w,h))
            else:
                last_y = y + h
        else:
            last_y = y + h

    diff_y = [lines_del[i][1] - lines_del[i - 1][1] for i in range(1, len(lines_del))]
    indixes = [i for i in range(len(diff_y)) if diff_y[i] > AVG_HEIGHT]

    last = 0
    lines = []

    for i in indixes:
        x,y,w,h = lines_del[i]
        cv2.rectangle(im2, (0, last), (WIDTH, y + h), (0, 255, 0), 2)
        lines.append((last, y + h))
        last = y+h

    lines.append((last, im2.shape[0] - 1))
    cv2.rectangle(im2, (0, last), (WIDTH, im2.shape[0]), (0, 255, 0), 2)

    os.chdir(os.path.join(BASE_DIR, "model", "temp"))

    names = []

    for ind,line in enumerate(lines):
        crop_img = img[line[0]:line[1], 0:WIDTH]
        cv2.imwrite('segmented_'+str(ind)+'.jpg', crop_img)
        names.append(os.path.join(BASE_DIR, "model", "temp", 'segmented_'+str(ind)+'.jpg'))

    os.chdir(BASE_DIR)
    return names


def cropped_img_path(img_name, BASE_DIR):
    print(BASE_DIR)
    split = str(img_name).split('/')
    path = os.path.join(BASE_DIR, split[0], split[1], split[2])
    print(path)

    # return segmentation(path, BASE_DIR)
    return seg_image(path, BASE_DIR)

