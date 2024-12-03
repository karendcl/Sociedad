# import opencv
import cv2
import sys, os, pathlib

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

    return segmentation(path, BASE_DIR)

