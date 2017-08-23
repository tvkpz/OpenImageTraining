#!/usr/bin/python
import logging
import multiprocessing
import os
import sys
import time
import timeit
from logging import StreamHandler
from multiprocessing import Process, Queue

import cv2
import psycopg2
import requests
from lxml.etree import Error
from pip._vendor.distlib._backport import shutil

from config import config
from psycopg2.pool import ThreadedConnectionPool

output_annotation_dir = "/home/ubuntu/bob/" + time.strftime('%H%M%S', time.localtime()) + "/"
os.mkdir(output_annotation_dir)

db_con_params = config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(StreamHandler(sys.stdout))

pool = ThreadedConnectionPool(minconn=1, maxconn=40, **db_con_params)


def connect():
    logger.debug('Connecting to the PostgreSQL database...')
    # conn = psycopg2.connect(**db_con_params)
    logger.debug('Connected...')

    conn = pool.getconn()

    return conn


def worker(image_url, image_id, class_description):
    image_name = image_url.split('/')[-1]
    print(image_name)

    img = cv2.imread("/openimg/2017_07/train/images/" + image_name)
    if img is None:
        img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
        if img is None:
            try:
                get = requests.get(image_url)
                with open("/openimg2/OpenImages/JPEGImages/" + image_name, 'wb') as f:
                    f.write(get.content)
            except Error as e:
                logger.error('Error: Can not download image ' + image_name + ", error; " + e)
                return

            try:
                img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
            except Error as e:
                logger.error(
                    'Error: File does not exist and will not be included in training: ' + image_name + ", error; " + e)
                return

    try:
        ht, wd, ch = img.shape
    except:
        print("Invalid image")
        pass

    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT ah.class_id, ah.x_min, ah.x_max, ah.y_min, ah.y_max "
        "FROM annotations_human_bbox AS ah INNER JOIN images_info "
        "ON ah.image_id=images_info.image_id WHERE images_info.image_id='" + image_id + "'")
    anno_infos = cur.fetchall()

    if len(anno_infos) == 0:
        return

    anno_file = image_name.split('.')[0] + ".xml"
    with open(output_annotation_dir + anno_file, "w") as f:
        f.write("<annotation>\n")
        f.write("\t<filename>" + image_name + "</filename>")
        f.write("\t<folder>OpenImages</folder>")
        for anno in anno_infos:
            f.write("\t<object>")
            f.write("\t\t<name>" + class_description[anno[0]] + "</name>")
            f.write("\t\t<bndbox>")
            f.write("\t\t\t<xmax>" + str(int(wd * float(anno[2]))) + "</xmax>")
            f.write("\t\t\t<xmin>" + str(int(wd * float(anno[1]))) + "</xmin>")
            f.write("\t\t\t<ymax>" + str(int(ht * float(anno[4]))) + "</ymax>")
            f.write("\t\t\t<ymin>" + str(int(ht * float(anno[3]))) + "</ymin>")
            f.write("\t\t</bndbox>")
            f.write("\t\t<pose>Unspecified</pose>")
            f.write("\t</object>\n")

        f.write("\t<size>\n")
        f.write("\t\t<depth>" + str(ch) + "</depth>\n")
        f.write("\t\t<height>" + str(ht) + "</height>\n")
        f.write("\t\t<width>" + str(wd) + "</width>\n")
        f.write("\t</size>\n")
        f.write("\t<source>\n")
        f.write("\t\t<annotation>Open Images 2017</annotation>\n")
        f.write("\t\t<database>The Open Image Dataset</database>\n")
        f.write("\t\t<image>flickr</image>\n")
        f.write("\t</source>\n")
        f.write("</annotation>\n")

    # close the communication with the PostgreSQL
    cur.close()
    conn.close()
    print('Database connection closed.')


def process():
    cores = (multiprocessing.cpu_count() - 1)
    pool = multiprocessing.Pool(cores - 1)
    for image_url, image_id in images:
        # multiprocessing.log_to_stderr(logging.DEBUG)
        jobs = pool.apply_async(worker, (image_url, image_id, class_description))
    pool.close()
    pool.join()
    jobs.get()


def get_all_anno():
    start = time.time()
    logger.info("Getting all annotations")

    get_all = "SELECT class_id, x_min, x_max, y_min, y_max FROM annotations_human_bbox"
    cur.execute(get_all)
    fetchall = cur.fetchall()

    time_taken = time.time() - start
    logger.info("Finish getting all annotations, taken %s seconds" % time_taken)

    return fetchall


record_no = 1000

if __name__ == '__main__':
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(1) FROM (SELECT DISTINCT image_id FROM annotations_human_bbox) AS a")
    images = cur.fetchall()
    logger.info("Total number of images: " + str(images[0][0]))

    cur.execute("SELECT class_description.class_id, class_description.class_desc FROM class_description")
    classes = cur.fetchall()

    logger.info("Total number of classes: " + str(classes[0][0]))

    class_description = {}
    for r in classes:
        class_description[r[0]] = r[1]

    cur.close()
    conn.close()

    timeit_timeit = timeit.timeit(lambda: process(), number=1)

    print(timeit_timeit)
    print("DONE")
    shutil.rmtree(output_annotation_dir)
