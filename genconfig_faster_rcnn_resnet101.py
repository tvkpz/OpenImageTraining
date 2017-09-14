
import tensorflow as tf
import os

flags = tf.app.flags()

flags.DEFINE_string('num_classes', 1, 'Number of object categories')
flags.DEFINE_string('pre_trained_model_path', None, 'Path to pre-trained ckpt files (do not add trailing /')
flags.DEFINE_string('train_tfrecord_path', None, 'Path/train_filename.record')
flags.DEFINE_string('val_tfrecord_path', None, 'Path/val_filename.record')
flags.DEFINE_string('label_map_path', None, 'path to .pbtxt category-index map file')
flags.DEFINE_string('config_path', None, 'output directory for config file')

FLAGS = flags.FLAGS

def set_config(num_classes, pre_trained_model_path, 
  train_tfrecord_path, val_tfrecord_path, label_map_path, config_path):

  if not os.path.exists(config_path):
    print("config path foes not exist")
    return -1
  if not os.path.exists(pre_trained_model_path+'model.ckpt'):
    print("model.ckpt file does not exist")
    return -1
  if not os.path.exists(train_tfrecord_path):
    print("train tfrecord file does not exist")
    return -1
  if not os.path.exists(val_tfrecord_path):
    print("validation tfrecord file does not exist")
    return -1
  if not os.path.exists(label_map_path):
    print("label map path does not exist")
    return -1
  if num_classes <= 0:
    print("Illegal number of classes")
    return -1


  with open(config_path+'/faster_rcnn_resnet101_voc07.config','w') as f:
  	f.write('# Faster R-CNN with Resnet-101 (v1), configured for Open Images Dataset.')
  	f.write('# Users should configure the fine_tune_checkpoint field in the train config as')
  	f.write('# well as the label_map_path and input_path fields in the train_input_reader and')
  	f.write('# eval_input_reader. Search for "PATH_TO_BE_CONFIGURED" to find the fields that')
  	f.write('# should be configured.')

  	f.write('model {')
    f.write('  faster_rcnn {')
    f.write('    num_classes: '+str(num_classes))    
    f.write('    image_resizer {')
    f.write('      keep_aspect_ratio_resizer {')
    f.write('        min_dimension: 600')
    f.write('        max_dimension: 1024')
    f.write('      }')
    f.write('    }')
    f.write('    feature_extractor {')
    f.write('      type: \'faster_rcnn_resnet101\'')
    f.write('      first_stage_features_stride: 16')
    f.write('    }')
    f.write('    first_stage_anchor_generator {')
    f.write('      grid_anchor_generator {')
    f.write('        scales: [0.25, 0.5, 1.0, 2.0]')
    f.write('        aspect_ratios: [0.5, 1.0, 2.0]')
    f.write('        height_stride: 16')
    f.write('        width_stride: 16')
    f.write('      }')
    f.write('    }')
    f.write('    first_stage_box_predictor_conv_hyperparams {')
    f.write('      op: CONV')
    f.write('      regularizer {')
    f.write('        l2_regularizer {')
    f.write('          weight: 0.0')
    f.write('        }')
    f.write('      }')
    f.write('      initializer {')
    f.write('        truncated_normal_initializer {')
    f.write('          stddev: 0.01')
    f.write('        }')
    f.write('      }')
    f.write('    }')
    f.write('    first_stage_nms_score_threshold: 0.0')
    f.write('    first_stage_nms_iou_threshold: 0.7')
    f.write('    first_stage_max_proposals: 300')
    f.write('    first_stage_localization_loss_weight: 2.0')
    f.write('    first_stage_objectness_loss_weight: 1.0')
    f.write('    initial_crop_size: 14')
    f.write('    maxpool_kernel_size: 2')
    f.write('    maxpool_stride: 2')
    f.write('    second_stage_box_predictor {')
    f.write('      mask_rcnn_box_predictor {')
    f.write('        use_dropout: false')
    f.write('        dropout_keep_probability: 1.0')
    f.write('        fc_hyperparams {')
    f.write('          op: FC')
    f.write('          regularizer {')
    f.write('            l2_regularizer {')
    f.write('              weight: 0.0')
    f.write('            }')
    f.write('          }')
    f.write('          initializer {')
    f.write('            variance_scaling_initializer {')
    f.write('              factor: 1.0')
    f.write('              uniform: true')
    f.write('              mode: FAN_AVG')
    f.write('            }')
    f.write('          }')
    f.write('        }')
    f.write('      }')
    f.write('    }')
    f.write('    second_stage_post_processing {')
    f.write('      batch_non_max_suppression {')
    f.write('        score_threshold: 0.0')
    f.write('        iou_threshold: 0.6')
    f.write('        max_detections_per_class: 100')
    f.write('        max_total_detections: 300')
    f.write('      }')
    f.write('      score_converter: SOFTMAX')
    f.write('    }')
    f.write('    second_stage_localization_loss_weight: 2.0')
    f.write('    second_stage_classification_loss_weight: 1.0')
    f.write('  }')
    f.write('}')
    f.write('\n')

    f.write('train_config: {')
    f.write('  batch_size: 1')
    f.write('  optimizer {')
    f.write('    momentum_optimizer: {')
    f.write('      learning_rate: {')
    f.write('        manual_step_learning_rate {')
    f.write('          initial_learning_rate: 0.0001')
    f.write('          schedule {')
    f.write('            step: 0')
    f.write('            learning_rate: .0001')
    f.write('          }')
    f.write('          schedule {')
    f.write('            step: 500000')
    f.write('            learning_rate: .00001')
    f.write('          }')
    f.write('          schedule {')
    f.write('            step: 700000')
    f.write('            learning_rate: .000001')
    f.write('          }')
    f.write('        }')
    f.write('      }')
    f.write('      momentum_optimizer_value: 0.9')
    f.write('    }')
    f.write('    use_moving_average: false')
    f.write('  }')
    f.write('  gradient_clipping_by_norm: 10.0')
    f.write('  fine_tune_checkpoint: \"'+pre_trained_model_path+'/model.ckpt\"') # Add exception handling here
    f.write('  from_detection_checkpoint: true')
    f.write('  num_steps: '+str(200000))
    f.write('  data_augmentation_options {')
    f.write('    random_horizontal_flip {')
    f.write('    }')
    f.write('  }')
    f.write('}')
    f.write('\n')

    f.write('train_input_reader: {')
    f.write('  tf_record_input_reader {')
    f.write('    input_path: \"'+train_tfrecord_path+'/train.record\"')
    f.write('  }')
    f.write('  label_map_path: \"'+label_map_path+'/label_map.pbtxt\"')
    f.write('}')
    f.write('\n')

    f.write('eval_config: {')
    f.write('  num_examples: 4952')
    f.write('}')
    f.write('\n')

    f.write('eval_input_reader: {')
    f.write('  tf_record_input_reader {')
    f.write('    input_path: \"'+val_tfrecord_path+'/val.record\"')
    f.write('  }')
    f.write('  label_map_path: \"'+label_map_path+'/label_map.pbtxt\"')
    f.write('  shuffle: false')
    f.write('  num_readers: 1')
    f.write('}')

    return 1

def main():

  assert FLAGS.num_classes, 'number of classes is missing'
  assert FLAGS.pre_trained_model_path, 'pre-trained model path missing'
  assert FLAGS.train_tfrecord_path, 'tfrecord path for train data missing'
  assert FLAGS.val_tfrecord_path, 'tfrecord path for validation data missing'
  assert FLAGS.config_path, 'dir path to output config file missing'

  status = set_config(FLAGS.num_classes, pre_trained_model_path, 
    FLAGS.train_tfrecord_path, FLAGS.val_tfrecord_path, 
    FLAGS.label_map_path, FLAGS.config_path)

  if status ~= 1:
    print("Config file not created ....")
  else:
    print(FLAGS.config_path+'/faster_rcnn_resnet101_voc07.config'+'...created')

if __name__ = '__main__':
  tf.app.run()


