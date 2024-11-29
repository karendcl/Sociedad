# import opencv
import cv2
import sys, os, pathlib



def line_already_found(lines_found, y, h):
    lines_copy = lines_found.copy()

    #if the line found is completely inside a line already found
    for line in lines_found:
        if y >= line[0] and y+h <= line[1]:
            return True, lines_found

    #if the line already found is completely inside the line found
    for ind,line in enumerate(lines_found):
        if y <= line[0] and y+h >= line[1]:
            lines_copy[ind] = (y, y+h)
            return True, lines_copy

    #if the line found is partially inside a line already found
    for ind,line in enumerate(lines_found):
        if y >= line[0] and y <= line[1]:
            lines_copy[ind] = (line[0], y+h)
            return True, lines_copy
        if y+h >= line[0] and y+h <= line[1]:
            lines_copy[ind] = (y, line[1])
            return True, lines_copy

    return False, lines_found

def final_retouch_of_bboxes(lines_found):
    lines_copy = lines_found.copy()
    lines_found = sorted(lines_found, key=lambda x: x[0])
    lines_copy = sorted(lines_copy, key=lambda x: x[0])

    to_remove = []

#     find overlapping bboxes
    for ind, line in enumerate(lines_found):
        if ind == 0:
            continue
        prev_start = lines_copy[ind-1][0]
        prev_end = lines_copy[ind-1][1]
        cur_start = lines_copy[ind][0]
        cur_end = lines_copy[ind][1]

        if cur_start <= prev_end and (prev_end - cur_start) < 0.9*(prev_end-prev_start):
            pass
        else:
            to_remove.append(ind-1)
            #edit the current to increase the bbox
            tuple = (prev_start, cur_end)
            lines_copy[ind] = tuple

    to_remove = sorted(to_remove, reverse=True)

    for index in to_remove:
        lines_copy.pop(index)

    #find avg height
    heights = [f-s for s,f in lines_copy]
    avg_height = sum(heights)/len(heights)

    #remove bboxes that are too small
    to_remove = []
    for ind, line in enumerate(lines_copy):
        if line[1] - line[0] < 0.4*avg_height:
            to_remove.append(ind)

    to_remove = sorted(to_remove, reverse=True)
    for index in to_remove:
        lines_copy.pop(index)


    return lines_copy

def segmentation(img_path, BASE_DIR):

    img = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh2 = cv2.threshold(img_gray, 50, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilation = cv2.dilate(thresh2, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    im2 = img.copy()

    #sort contours by position relative to the x-axis (top to bottom)
    # contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[1])

    lines_found = []

    #order the contours by the height
    contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[3])

    #see the width of the image
    width = im2.shape[1]

    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        #if the line is already found, skip it
        found, lines_found = line_already_found(lines_found, y, h)
        if found:
            continue
        lines_found.append((y,y+h))

    lines_found = final_retouch_of_bboxes(lines_found)
    #draw the rectangle
    for line in lines_found:
        cv2.rectangle(im2, (0, line[0]), (width, line[1]), (0, 255, 0), 2)

    os.chdir(os.path.join(BASE_DIR, "model", "temp"))

    cv2.imwrite('segmented.jpg', im2)

    names = []
    #crop the image
    for ind, line in enumerate(lines_found):
        crop_img = img[line[0]:line[1], 0:width]
        cv2.imwrite('segmented_'+str(ind)+'.jpg', crop_img)
        names.append('segmented_'+str(ind)+'.jpg')

    os.chdir(BASE_DIR)

    return names


def cropped_img_path(img_name, BASE_DIR):
    print(BASE_DIR)
    split = str(img_name).split('/')
    path = os.path.join(BASE_DIR, split[0], split[1], split[2])
    print(path)


    return segmentation(path, BASE_DIR)

