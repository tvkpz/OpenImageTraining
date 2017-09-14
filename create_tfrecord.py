
import pandas as pd
import temsorflow as tf
from lxml import etree

flags = tf.app.flags()

#flags.DEFINE_string('anno_train_file_name', None, 'Annotation training csv file')
#flags.DEFINE_string('anno_val_file_name', None, 'Annotation validation csv file')
flags.DEFINE_string('annotation_file_name', None, 'file path of annotation csv')
flags.DEFINE_string('train_split', 0.8, 'Value between [0,1]')
flags.DEFINE_string('label_map_path', None, 'path to otuput .pbtxt category-index map file')
flags.DEFINE_string('output_tfrecord_dir', None, 'output tfrecord directory')
flags.DEFINE_string('data_dir', None, 'root directory of data')

FLAGS = flags.FLAGS

def create_label_map(category_list, map_path):
	"""Create category-index map file"""
	label_map_dict = {}
	with open(map_path+'/label_map.pbtxt','w') as f:
		count=1
		for label in category_list:
			f.write('item {\n')
			f.write('\tid: 'str(count)+'\n')
			f.write('\tname: '+label+'\n')
			f.write('}\n')
			label_map_dict[label] = count
			count=count+1

	return label_map_dict

def dict_to_tf_example(data,
	dataset_directory,
	label_map_dict,
	ignore_difficult_instances=False,
	image_subdirectory='JPEGImages'):

	img_path = os.path.join(data['folder'], image_subdirectory, data['filename'])
	full_path = os.path.join(dataset_directory, img_path)
	with tf.gfile.GFile(full_path, 'rb') as fid:
    	encoded_jpg = fid.read()
		encoded_jpg_io = io.BytesIO(encoded_jpg)
	image = PIL.Image.open(encoded_jpg_io)
	if image.format != 'JPEG':
 		raise ValueError('Image format not JPEG')
	key = hashlib.sha256(encoded_jpg).hexdigest()

	width = int(data['size']['width'])
	height = int(data['size']['height'])

	xmin = []
	ymin = []
	xmax = []
	ymax = []
	classes = []
	classes_text = []
	truncated = []
	poses = []
	difficult_obj = []
	for obj in data['object']:
		difficult = bool(int(obj['difficult']))
		if ignore_difficult_instances and difficult:
			continue

		difficult_obj.append(int(difficult))

 		xmin.append(float(obj['bndbox']['xmin']) / width)
		ymin.append(float(obj['bndbox']['ymin']) / height)
		xmax.append(float(obj['bndbox']['xmax']) / width)
		ymax.append(float(obj['bndbox']['ymax']) / height)
		classes_text.append(obj['name'].encode('utf8'))
		classes.append(label_map_dict[obj['name']])
		truncated.append(int(obj['truncated']))
		poses.append(obj['pose'].encode('utf8'))

	example = tf.train.Example(features=tf.train.Features(feature={
    	'image/height': dataset_util.int64_feature(height),
    	'image/width': dataset_util.int64_feature(width),
    	'image/filename': dataset_util.bytes_feature(
         	data['filename'].encode('utf8')),
    	'image/source_id': dataset_util.bytes_feature(
        	data['filename'].encode('utf8')),
      	'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
      	'image/encoded': dataset_util.bytes_feature(encoded_jpg),
      	'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
      	'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
      	'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
      	'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
      	'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
      	'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
      	'image/object/class/label': dataset_util.int64_list_feature(classes),
      	'image/object/difficult': dataset_util.int64_list_feature(difficult_obj),
      	'image/object/truncated': dataset_util.int64_list_feature(truncated),
      	'image/object/view': dataset_util.bytes_list_feature(poses),
  	}))
  	return example


def main():
	"""Main Function"""

	#assert FLAGS.train_split, 'train_split information is missing'
	assert FLAGS.annotation_file_name, 'file path of annotation csv'
	assert FLAGS.label_map_path, 'output dir for label_map file missing'
	assert FLAGS.output_tfrecord_dir, 'output path for tfrecord directory missing'
	assert FLAGS.data_dir, 'root directory of data missing'

	if not os.path.exists(FLAGS.annotation_file_name):
		print("annotation file name does not exist")
		return -1
	if not os.path.exists(FLAGS.label_map_path):
		print("config path does not exist")
		return -1
	if not os.path.exists(FLAGS.output_tfrecord_dir):
		print("the output dir for writing tfrecord does not exist")
		return -1
	if not os.path.exists(FLAGS.data_dir):
		print("the root directory for data does not exist")

	writer_train = tf.python_io.TFRecordWriter(FLAGS.output_tfrecord_dir+'/train.record')
	writer_eval = tf.python_io.TFRecordWriter(FLAGS.output_tfrecord_dir+'/eval.record')

	df = pd.read_csv(FLAGS.annotation_file_name,sep=',',
		names=["name","height","width","label","xmin","ymin","xmax","ymax"])

	#df.reindex(np.random.permutation(df.index))
	#df = df.sample(frac=1).reset_index(drop=True)

	filenames = df.name.unique()
	total_count = len(filenames)
	label_map_dict = create_label_map(df.label.unique(), label_map_path)

	groupby_image=df['label'].groupby(df['name'])
	# shuffle the examples by name
	#groupby_image.reindex(np.random.permutation(groupby_image.index))

	#write train.tfrecord

	train_count = 0
	for name, group in groupby_image:
		data = {}
		data['folder'] = data_dir+'/traineval-data'
		data['filename'] = name+'.jpg'
		data['size']['width'] = group.width
		data['size']['height'] = group.height
		data['object'] = []
		for index, row in group.iterrows():
			obj = {}
			obj['bndbox']['xmin'] = row['xmin']
			obj['bndbox']['xmax'] = row['xmax']
			obj['bndbox']['ymin'] = row['ymin']
			obj['bndbox']['ymax'] = row['ymax']
			obj['name'] = row['label']
			data['object'].append(obj)

		example = dict_to_tf_example(data, data_dir, label_map_dict)
		if train_count < train_split*total_count:
			writer_train.write(example.SerializeToString())
			train_count+=1
		else:
			writer_train.write(example.SerializeToString())

	writer_train.close()
	writer_eval.close()


if __name__ == '__main__':
    main()


