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
'''
<annotation>
	<filename>14114289630_e5951693e5_o.jpg</filename>
	<folder>OpenImages</folder>
	<object>
		<name>Person</name>
		<bndbox>
			<xmax>1598</xmax>
			<xmin>1096</xmin>
			<ymax>1416</ymax>
			<ymin>493</ymin>
		</bndbox>
		<pose>Unspecified</pose>
	</object>
	<size>
		<depth>3</depth>
		<height>2136</height>
		<width>3216</width>
	</size>
	<source>
		<annotation>Open Images 2017</annotation>
		<database>The Open Image Dataset</database>
		<image>flickr</image>
	</source>
</annotation>
'''

dir_ = "/home/ubuntu/bob/testbenchmark" + time.strftime('%H%M%S', time.localtime()) + "/"
os.mkdir(dir_)


def objectCreate(row):
    class_name = row[0]
    xmax = str(int(wd * float(row[2])))
    xmin = str(int(wd * float(row[1])))
    ymax = str(int(ht * float(row[4])))
    ymin = str(int(ht * float(row[3])))
    return """
<object>
    <name>%s</name>
    <bndbox>
        <xmax>%s</xmax>
        <xmin>%s</xmin>
        <ymax>%s</ymax>
        <ymin>%s</ymin>
    </bndbox>
    <pose>Unspecified</pose>
</object>""" % (class_name, xmax, xmin, ymax, ymin)


def method_name():
    for file_name in range(1, 10000):
        with open(dir_ + str(file_name), "w") as f:
            objects = "".join([objectCreate(row) for row in anno_info])
            string = """
<annotation>
    <filename>%s</filename>
    <folder>OpenImages</folder>
        %s
    <size>
        <depth>%s</depth>
        <height>%s</height>
        <width>%s</width>
    </size>
    <source>
        <annotation>Open Images 2017</annotation>
        <database>The Open Image Dataset</database>
        <image>flickr</image>
    </source>
</annotation>""" % (image_name, objects, ch_str, ht_str, wd_str)
            f.write(string)


method_name()
timeit_timeit = timeit.timeit(lambda: method_name(), number=1)

print(timeit_timeit)
print("DONE")
shutil.rmtree(dir_)
