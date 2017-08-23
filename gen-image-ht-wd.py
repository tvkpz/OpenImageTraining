#!/usr/bin/python
import psycopg2
from config import config
import cv2
import urllib
from subprocess import call
from subprocess import check_output
import multiprocessing, logging
 
def connect(conn=None):
    """ Connect to the PostgreSQL database server """
    #conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    #finally:
    #    if conn is not None:
    #        conn.close()
    #        print('Database connection closed.')

def worker(image_url):

    image_name = image_url[0].split('/')[-1]
    print(image_name)

    img=cv2.imread("/openimg/2017_07/train/images/"+image_name) 
    if img is None:
        testfile = urllib.URLopener()
        try:
            testfile.retrieve(res[0], "/openimg2/OpenImages/JPEGImages/"+image_name)
            img=cv2.imread("/openimg2/OpenImages/JPEGImages/"+image_name)
        except:
            print('Error: File does not exist and will not be included in training')
            return
    else:
        call(["mv","/openimg/2017_07/train/images/"+image_name,"/openimg2/OpenImages/JPEGImages/"+image_name])
    
    ht,wd,ch = img.shape
    #print(img.shape)

    conn = connect()
    # create a cursor
    cur = conn.cursor()
    cur.execute("UPDATE images_info set width = "+wd+", height = "+height+", channel = "+ch+" where images_info.original_url="+image_url)

    # close the communication with the PostgreSQL
    cur.close()
    conn.close()
    print('Database connection closed.')
    return

 
if __name__ == '__main__':
    conn = connect()
    # create a cursor
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT images_info.original_url FROM images_info")
    image_list = cur.fetchall()
    print(len(imageid_list))
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()

    cores = (multiprocessing.cpu_count()-1)
    pool = multiprocessing.Pool(cores)
    for image_url in image_list:       
        multiprocessing.log_to_stderr(logging.DEBUG)
        #p = multiprocessing.Process(target=worker, args=(image_id,person_id,))
        jobs = pool.apply_async(worker, (image_url))
        #jobs.append(p)
        #p.start()

    pool.close()
    pool.join()
    jobs.get()


