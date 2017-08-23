#!/usr/bin/python
import psycopg2
from config import config
import cv2
import urllib
from subprocess import call
from subprocess import check_output
import multiprocessing, logging
import pdb


def connect(conn=None):
    """ Connect to the PostgreSQL database server """
    # conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        # finally:
        #    if conn is not None:
        #        conn.close()
        #        print('Database connection closed.')


def worker(image_url, image_id, class_description):
    image_name = image_url.split('/')[-1]
    print(image_name)

    try:
        img = cv2.imread("/openimg/2017_07/train/images/" + image_name)
    except:
        try:
            img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
        except:
            testfile = urllib.URLopener()
            try:
                testfile.retrieve(image_url, "/openimg2/OpenImages/JPEGImages/" + image_name)
                img = cv2.imread("/openimg2/OpenImages/JPEGImages/" + image_name)
            except:
                print('Error: File does not exist and will not be included in training')
                return

    # else:
    #    call(["mv","/openimg/2017_07/train/images/"+image_name,"/openimg2/OpenImages/JPEGImages/"+image_name])

    ht, wd, ch = img.shape
    # print(img.shape)

    conn = connect()
    # create a cursor
    cur = conn.cursor()
    # cur.execute("UPDATE images_info set width = "+wd+", height = "+height+", channel = "+ch+" where images_info.original_url="+image_url)
    try:
        cur.execute(
            "SELECT ah.class_id, ah.x_min, ah.x_max, ah.y_min, ah.y_max FROM annotations_human_bbox AS ah INNER JOIN images_info ON annotations_human_bbox.image_id=images_info.image_id WHERE images_info.image_id='" + image_id + "'")
    except:
        print("error")
    anno_info = cur.fetchall()
    anno_file = image_name.split('.')[0] + ".xml"
    with open("/openimg2/OpenImages/Annotations/" + anno_file, "w") as f:
        f.write("<annotation>\n")
        f.write("\t<filename>" + image_name + "</filename>")
        f.write("\t<folder>OpenImages</folder>")
        for anno in anno_info:
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
    return


if __name__ == '__main__':
    conn = connect()
    # create a cursor
    cur = conn.cursor()

    cur.execute("SELECT images_info.original_url, images_info.image_id FROM images_info")
    imageinfo_list = cur.fetchall()

    cur.execute("SELECT class_description.class_id, class_description.class_desc FROM class_description")
    res = cur.fetchall()
    class_description = {}
    for r in res:
        class_description[r[0]] = r[1]

    # close the communication with the PostgreSQL
    cur.close()
    conn.close()

    cores = (multiprocessing.cpu_count() - 1)
    pool = multiprocessing.Pool(cores)
    for image_url, image_id in imageinfo_list:
        multiprocessing.log_to_stderr(logging.DEBUG)
        # pdb.set_trace()
        # p = multiprocessing.Process(target=worker, args=(image_id,person_id,))
        jobs = pool.apply_async(worker, (image_url, image_id, class_description))
        # jobs.append(p)
        # p.start()

    pool.close()
    pool.join()
    jobs.get()
