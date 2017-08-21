#!/usr/bin/python
import psycopg2
from config import config
import cv2
import urllib
from subprocess import call
 
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

 
if __name__ == '__main__':
    conn = connect()
    # create a cursor
    cur = conn.cursor()

    cur.execute("SELECT class_id FROM class_description WHERE class_desc='Person'")
    res = cur.fetchone()
    person_id = res[0]
    print(person_id) 
    cur.execute("SELECT DISTINCT annotations_human_bbox.image_id FROM annotations_human_bbox WHERE class_id='"+person_id+"'")
    imageid_list = cur.fetchall()
    print(len(imageid_list))

    # execute a statement
    #print('PostgreSQL database version:')
    #cur.execute('SELECT version()')
    #cur.execute("SELECT images_info.original_url, group_anno_table.image_id, group_anno_table.class_id, group_anno_table.x_min, group_anno_table.y_min, group_anno_table.x_max, group_anno_table.y_max FROM class_description, images_info, (SELECT * FROM annotations_human_bbox GROUP BY annotations_human_bbox.image_id) AS group_anno_table WHERE ((class_description.class_desc='Person' AND class_description.class_id=group_anno_table.class_id) AND group_anno_table.image_id=images_info.image_id)") 
    #cur.execute("SELECT final_table.image_id, combine(final_table.original_url, final_table.class_id, final_table.x_min, final_table.y_min, final_table.x_max, final_table.y_max) FROM (SELECT images_info.original_url, annotations_human_bbox.image_id, annotations_human_bbox.class_id, annotations_human_bbox.x_min, annotations_human_bbox.y_min, annotations_human_bbox.x_max, annotations_human_bbox.y_max FROM annotations_human_bbox, class_description, images_info WHERE ((class_description.class_desc='Person' AND class_description.class_id=annotations_human_bbox.class_id) AND annotations_human_bbox.image_id=images_info.image_id)) AS final_table  GROUP BY final_table.image_id")
    #cur.execute("SELECT n1.image_id, n1.class_id, n1.x_min, n1.y_min, n1.x_max, n1.y_max FROM (SELECT image_id, class_id, x_min, y_min, x_max, y_max FROM annotations_human_bbox GROUP BY image_id) n1 INNER JOIN (SELECT class_id FROM class_description) n2 ON (n1.class_id = n2.class_id AND n2.class_desc = 'Person')")

    count=0
    for image_id in imageid_list:
        cur.execute("SELECT images_info.original_url FROM images_info WHERE images_info.image_id='"+image_id[0]+"'")
        res = cur.fetchone()
        image_name = res[0].split('/')[-1]
        print(image_name)

        img=cv2.imread("/openimg/2017_07/train/images/"+image_name) 
        if img is None:
            testfile = urllib.URLopener()
            testfile.retrieve(res[0], "/openimg2/OpenImages/JPEGImages/"+image_name)
            img=cv2.imread("/openimg2/OpenImages/JPEGImages/"+image_name)
        else:
            call(["mv","/openimg/2017_07/train/images/"+image_name,"/openimg2/OpenImages/JPEGImages/"+image_name])
            ht,wd,ch = img.shape
        print(img.shape)
        with open("/openimg2/OpenImages/ImageSets/Main/images_train.txt","a") as f1:
            f1.write(image_name.split('.')[0]+"\n")
        with open("/openimg2/OpenImages/ImageSets/Main/person_train.txt","a") as f2:
            f2.write(image_name.split('.')[0]+" 1\n")

        cur.execute("SELECT annotations_human_bbox.x_min, annotations_human_bbox.y_min, annotations_human_bbox.x_max, annotations_human_bbox.y_max FROM annotations_human_bbox WHERE annotations_human_bbox.class_id='"+person_id+"' AND annotations_human_bbox.image_id='"+image_id[0]+"'")
        rows = cur.fetchall()
        print("no. of objects = "+str(len(rows)))
        anno_file = image_name.split('.')[0]+".xml"
        with open("/openimg2/OpenImages/Annotations/"+anno_file,"w") as f:
            f.write("<annotation>\n")
            f.write("\t<filename>"+image_name+"</filename>")
            f.write("\t<folder>OpenImages</folder>")

            for row in rows:
                print(row)
                f.write("\t<object>")
                f.write("\t\t<name>Person</name>")
                f.write("\t\t<bndbox>")
                f.write("\t\t\t<xmax>"+str(int(wd*float(row[2])))+"</xmax>")
                f.write("\t\t\t<xmin>"+str(int(wd*float(row[0])))+"</xmin>")
                f.write("\t\t\t<ymax>"+str(int(ht*float(row[3])))+"</ymax>")
                f.write("\t\t\t<ymin>"+str(int(ht*float(row[1])))+"</ymin>")
                f.write("\t\t</bndbox>")
                f.write("\t\t<pose>Unspecified</pose>")
                f.write("\t</object>\n")

            f.write("\t<size>\n")
            f.write("\t\t<depth>"+str(ch)+"</depth>\n")
            f.write("\t\t<height>"+str(ht)+"</height>\n")
            f.write("\t\t<width>"+str(wd)+"</width>\n")
            f.write("\t</size>\n")
            f.write("\t<source>\n")
            f.write("\t\t<annotation>Open Images 2017</annotation>\n")
            f.write("\t\t<database>The Open Image Dataset</database>\n")
            f.write("\t\t<image>flickr</image>\n")
            f.write("\t</source>\n")
            f.write("</annotation>\n")
            count=count+1

        if count > 20:
            break





    # display the PostgreSQL database server version
    #db_version = cur.fetchone()
    #print(db_version)

    # close the communication with the PostgreSQL
    cur.close()

    conn.close()
    print('Database connection closed.')
'''    
    <annotation>
        <filename>2012_004331.jpg</filename>
        <folder>VOC2012</folder>
        <object>
                <name>person</name>
                <actions>
                        <jumping>1</jumping>
                        <other>0</other>
                        <phoning>0</phoning>
                        <playinginstrument>0</playinginstrument>
                        <reading>0</reading>
                        <ridingbike>0</ridingbike>
                        <ridinghorse>0</ridinghorse>
                        <running>0</running>
                        <takingphoto>0</takingphoto>
                        <usingcomputer>0</usingcomputer>
                        <walking>0</walking>
                </actions>
                <bndbox>
                        <xmax>208</xmax>
                        <xmin>102</xmin>
                        <ymax>230</ymax>
                        <ymin>25</ymin>
                </bndbox>
                <difficult>0</difficult>
                <pose>Unspecified</pose>
                <point>
                        <x>155</x>
                        <y>119</y>
                </point>
        </object>
        <segmented>0</segmented>
        <size>
                <depth>3</depth>
                <height>375</height>
                <width>500</width>
        </size>
        <source>
                <annotation>PASCAL VOC2012</annotation>
                <database>The VOC2012 Database</database>
                <image>flickr</image>
        </source>
</annotation>
'''



