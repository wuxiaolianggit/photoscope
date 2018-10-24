#!/usr/bin/env python
import os
import cv2
import numpy as np
import time
from glob import glob
from functools import partial
from flask import Flask
from flask import render_template, request, send_from_directory

app=Flask(__name__)

def color_hist(bins, img_pth):
    img = cv2.imread(img_pth, 0)
    hist = cv2.calcHist([img], [0], None, [bins], [0, 256])
    return hist / (sum(hist) + 1e-10)

def dist_calc(query_img, ref_img):
    return cv2.compareHist(query_img, ref_img, cv2.HISTCMP_CHISQR)

def transform_query(img_arr):
    hist = cv2.calcHist([img_arr], [0], None, [bins], [0, 256])
    return hist / (sum(hist) + 1e-10)

data_dir = '/path/to/images/'
bins = 128
num_results = 50

start = time.time()

img_lst = glob(data_dir + '*')
print('Calculating image features')
color_hist_ = partial(color_hist, bins)
corpus_features = list(map(color_hist_, img_lst)) # bottleneck

end = time.time()
elapsed = end - start
elapsed_fmt = time.strftime("%H:%M:%S", time.gmtime(elapsed))
print('Finished feature calculation in {}, beginning search...'.format(elapsed_fmt))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        data_files = request.files.getlist('file[]')
        for data_file in data_files:
            file_contents = data_file.read()
            img_array = cv2.imdecode(np.frombuffer(file_contents, np.uint8), -1)

	query_hist = transform_query(img_array)
	query_dist = partial(dist_calc, query_hist)
	result_dist = list(map(query_dist, corpus_features))
	result_paths = np.argsort(result_dist)[:num_results]
	result_paths = [img_lst[pth].split('/')[-1] for pth in result_paths]
	return render_template("results.html", result_paths=result_paths)
    return render_template("index.html")

@app.route('/image/<path:filename>')
def get_image(filename):
    return send_from_directory(data_dir, filename)

if __name__ == "__main__":
    app.run("0.0.0.0")