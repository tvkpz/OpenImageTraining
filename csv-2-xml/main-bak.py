#!/usr/bin/python
import logging
import multiprocessing
import os
import sys
import time
import timeit
from logging import StreamHandler

import cv2
import requests
from cv2 import cv2
from lxml.etree import Error
from pip._vendor.distlib._backport import shutil
from psycopg2.pool import ThreadedConnectionPool

from config import config

output_annotation_dir = "/home/ubuntu/bob/" + time.strftime('%H%M%S', time.localtime()) + "/"
os.mkdir(output_annotation_dir)

db_con_params = config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(StreamHandler(sys.stdout))

number_of_workers = int(multiprocessing.cpu_count() * 1.5 - 1)
logger.info("Using %s workers" % number_of_workers)
db_conn_pool = ThreadedConnectionPool(minconn=1, maxconn=number_of_workers + 5, **db_con_params)

record_no = 1000


# import cProfile


def get_db_conn():
    logger.debug('Getting DB con...')
    # conn = psycopg2.connect(**db_con_params)
    try:
        conn = db_conn_pool.getconn()
    except Error as e:
        logger.error("Error while getting connection: " + e.msg)
    logger.debug('Connected...')

    return conn


def worker(image_url, image_id, class_description):
    process_image(image_url, image_id, class_description)
    # process = multiprocessing.current_process()
    # cProfile.runctx("process_image(image_url, image_id, class_description)",
    #                 globals(), locals(),
    #                 'psstat/prof%s.pstat' % process.name)


def process_image(image_url, image_id, class_description):
    image_name = image_url.split('/')[-1]
    logger.debug("Processing " + image_name)

    img = cv2.imread("/openimg/2017_07/train/images/" + image_name)
    if img is None:
        img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
        if img is None:
            try:
                get = requests.get(image_url)
                with open("/openimg2/OpenImages/JPEGImages/" + image_name, 'wb') as f:
                    f.write(get.content)
            except Error as e:
                logger.error('Can not download image ' + image_name + ", error; " + e)
                return

            try:
                img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
            except Error as e:
                logger.error(
                    'File does not exist and will not be included in training: ' + image_name + ", error; " + e)
                return
    if img is None:
        logger.error('Invalid image' + image_name)
        return

    try:
        ht, wd, ch = img.shape
    except:
        logger.error("Invalid image")

    anno_infos = get_annotation_XXXXXX(image_id)

    write_2_xml_XXXXXXXXX(anno_infos, ch, class_description, ht, image_name, wd)


def write_2_xml_XXXXXXXXX(anno_infos, ch, class_description, ht, image_name, wd):
    anno_file = image_name.split('.')[0] + ".xml"
    with open(output_annotation_dir + anno_file, "w") as f:
        f.write("<annotation>\n")
        f.write("\t<filename>" + image_name + "</filename>\n")
        f.write("\t<folder>OpenImages</folder>\n")
        for anno in anno_infos:
            f.write("\t<object>\n")
            f.write("\t\t<name>" + class_description[anno[0]] + "</name>\n")
            f.write("\t\t<bndbox>\n")
            f.write("\t\t\t<xmax>" + str(int(wd * float(anno[2]))) + "</xmax>\n")
            f.write("\t\t\t<xmin>" + str(int(wd * float(anno[1]))) + "</xmin>\n")
            f.write("\t\t\t<ymax>" + str(int(ht * float(anno[4]))) + "</ymax>\n")
            f.write("\t\t\t<ymin>" + str(int(ht * float(anno[3]))) + "</ymin>\n")
            f.write("\t\t</bndbox>\n")
            f.write("\t\t<pose>Unspecified</pose>\n")
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


def get_annotation_XXXXXX(image_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT class_id, x_min, x_max, y_min, y_max "
        "FROM annotations_human_bbox WHERE image_id='" + image_id + "'")
    anno_infos = cur.fetchall()
    cur.close()
    db_conn_pool.putconn(conn)
    return anno_infos


def process():
    cores = (number_of_workers)
    multiprocessing_pool = multiprocessing.Pool(cores - 1)
    for image_url, image_id in images:
        # multiprocessing.log_to_stderr(logging.DEBUG)
        jobs = multiprocessing_pool.apply_async(worker, (image_url, image_id, classes_description))
    multiprocessing_pool.close()
    multiprocessing_pool.join()
    jobs.get()


def get_all_images():
    logger.info("Getting the images")
    start = time.time()

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT original_url, image_id FROM images_info WHERE image_id IN (SELECT DISTINCT image_id FROM annotations_human_bbox) LIMIT " + str(
            record_no))
    fetchall = cur.fetchall()
    db_conn_pool.putconn(conn)
    logger.info("Get images took %s s " % (time.time() - start))
    return fetchall


def get_all_classes():
    logger.info("Getting the classes")
    start = time.time()

    db_conn = get_db_conn()
    cur = db_conn.cursor()
    cur.execute("SELECT class_description.class_id, class_description.class_desc FROM class_description")
    fetchall = cur.fetchall()
    db_conn_pool.putconn(db_conn)

    logger.info("Get classes took %s s " % (time.time() - start))
    return fetchall


if __name__ == '__main__':

    images = get_all_images()
    number_of_images = len(images)

    logger.info("Total number of images: " + str(number_of_images))

    classes = get_all_classes()
    logger.info("Total number of classes: " + str(len(classes)))

    classes_description = {}
    for class_ in classes:
        classes_description[class_[0]] = class_[1]

    timeit_timeit = timeit.timeit(lambda: process(), number=1)

    average_time = timeit_timeit / record_no
    logger.info("Total time taken: " + str(timeit_timeit))
    logger.info("Speed: " + str(1 / average_time) + " images/second")
    logger.info("Will take " + str(int(669124 * average_time / 60)) + " minutes to finish 669124 images")

    logger.info("Clean up the output folder")
    shutil.rmtree(output_annotation_dir)
