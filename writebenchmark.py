import os
import timeit

import time

import shutil

anno_ = 'Person'
image_name = '14114289630_e5951693e5_o.jpg'
ch = 3
ht = 2136
wd = 3216
ch_str = str(3)
ht_str = str(2136)
wd_str = str(3216)
anno_info = [['Person', 1598, 1096, 1416, 493]]

dir_ = "/home/ubuntu/bob/testbenchmark" + time.strftime('%H%M%S', time.localtime()) + "/"
os.mkdir(dir_)


def method_name():
    for file_name in range(1, 10000):
        with open(dir_ + str(file_name), "w") as f:
            f.write("<annotation>\n")
            f.write("\t<filename>" + image_name + "</filename>")
            f.write("\t<folder>OpenImages</folder>")
            for anno in anno_info:
                xmax = str(int(wd * float(anno[2])))
                xmin = str(int(wd * float(anno[1])))
                ymax = str(int(ht * float(anno[4])))
                ymin = str(int(ht * float(anno[3])))
                class_name = "Person"

                f.write("\t<object>")
                f.write("\t\t<name>" + class_name + "</name>")
                f.write("\t\t<bndbox>")
                f.write("\t\t\t<xmax>" + xmax + "</xmax>")
                f.write("\t\t\t<xmin>" + xmin + "</xmin>")
                f.write("\t\t\t<ymax>" + ymax + "</ymax>")
                f.write("\t\t\t<ymin>" + ymin + "</ymin>")
                f.write("\t\t</bndbox>")
                f.write("\t\t<pose>Unspecified</pose>")
                f.write("\t</object>\n")

            f.write("\t<size>\n")

            f.write("\t\t<depth>" + ch_str + "</depth>\n")
            f.write("\t\t<height>" + ht_str + "</height>\n")
            f.write("\t\t<width>" + wd_str + "</width>\n")
            f.write("\t</size>\n")
            f.write("\t<source>\n")
            f.write("\t\t<annotation>Open Images 2017</annotation>\n")
            f.write("\t\t<database>The Open Image Dataset</database>\n")
            f.write("\t\t<image>flickr</image>\n")
            f.write("\t</source>\n")
            f.write("</annotation>\n")


method_name()

timeit_timeit = timeit.timeit(lambda: method_name(), number=1)

print(timeit_timeit)
print("DONE")

shutil.rmtree(dir_)
