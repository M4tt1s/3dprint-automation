import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser("3d printing auto-detouring tool")
    parser.add_argument("img_path", help="path to image")
    parser.add_argument("width", help="real life 3d piece width")
    args = parser.parse_args()

    img = cv.imread(args.img_path)
    if img is None or img.size == 0:
        raise Exception(f"Unable to read image {args.image}. Please check the path.")
    
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edge_img = cv.Canny(gray_img, threshold1=450, threshold2=600)

    ratio = int(args.width) / len(edge_img[0])

    path = []

    for i in range(len(edge_img)) :
        for j in range(len(edge_img[i])) :
            if edge_img[i][j] == 255 :
                path.append([i * ratio, j * ratio])

    data = np.array(path)
    
    np.save("path", path)
