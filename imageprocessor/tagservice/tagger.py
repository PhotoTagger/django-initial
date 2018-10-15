import os
import numpy as np
import tensorflow as tf
from PIL import Image
from .tfutils import label_map_util

_MODEL_NAME = 'ssd_mobilenet_v1_coco_2018_01_28'
_LABEL_MAP_NAME = 'mscoco_label_map.pbtxt'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
_PATH_TO_FROZEN_GRAPH = os.path.join('imageprocessor/tagservice/tfmodels', _MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map. The label map associates the output values of the model with real words
_PATH_TO_LABELS = os.path.join('imageprocessor/tagservice/tfmodels', _MODEL_NAME, _LABEL_MAP_NAME)

# The threshold of certainty above which we will return a tag
_THRESHOLD = 0.5

# reference to the tf session
_session: tf.Session = None
# reference to the model in memory
_detection_graph: tf.Graph  = None
# pointer to the label dictionary
_category_index = None
# references to input and output tensors of the detection graph
_image_tensor = None
_boxes_tensor = None
_scores_tensor = None
_classes_tensor = None
_num_detections_tensor = None

#oads the model into memory from disk
def _load_model():
    global _detection_graph 
    _detection_graph = tf.Graph()
    with _detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(_PATH_TO_FROZEN_GRAPH, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

#Loads the label map into memory from disk
def _load_labels():
    global _category_index
    _category_index = label_map_util.create_category_index_from_labelmap(_PATH_TO_LABELS, use_display_name=True)

#Creates a TF Session which will be used for all subsequent object detections
def _load_session():
    global _session, _image_tensor, _boxes_tensor, _scores_tensor, _classes_tensor, _num_detections_tensor
    _session = tf.Session(graph=_detection_graph)
    # Get references to all input and output tensors
    _image_tensor = _detection_graph.get_tensor_by_name('image_tensor:0')
    _boxes_tensor = _detection_graph.get_tensor_by_name('detection_boxes:0')
    _scores_tensor = _detection_graph.get_tensor_by_name('detection_scores:0')
    _classes_tensor = _detection_graph.get_tensor_by_name('detection_classes:0')
    _num_detections_tensor = _detection_graph.get_tensor_by_name('num_detections:0')

# converts a pillow Image into a numpy array that can be consumed by TF
def _load_image_into_numpy_array(image: Image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

# converts class number to class name
def _get_class_name(class_num: int):
    return _category_index[class_num]['name']

# performs the actual detection
def detect(image: Image):
    """Runs object detection to return a list of the objects in a given image
    
    Arguments:
        image {Image} -- Pillow Image Class
    
    Returns:
        list -- List of string tags
    """

    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_expanded = np.expand_dims(image, axis=0)
    # Actually perform the detection and stores them as multidimensional tensors
    (boxes, scores, classes, num_dectections) = _session.run(
        [_boxes_tensor, _scores_tensor, _classes_tensor, _num_detections_tensor],
        feed_dict={_image_tensor: image_expanded})

    # reduce the dimensions of each tensor into 1d arrays (hopefully)
    #boxes = np.squeeze(boxes)
    scores = np.squeeze(scores)
    classes = np.squeeze(classes).astype(np.int32)
    num_dectections = np.squeeze(num_dectections).astype(np.int32)

    tags = []
    for i in range(0, num_dectections):
        if scores[i] >= _THRESHOLD:
            tags.append(_get_class_name(classes[i]))
  
    return tags


if __name__ == "__main__":
    # Get the file name for every image in the test_images folder
    TEST_IMAGE_NAMES = [f for f in os.listdir('test_images') if os.path.isfile(os.path.join('test_images', f))]

    _PATH_TO_FROZEN_GRAPH = os.path.join('tfmodels', _MODEL_NAME, 'frozen_inference_graph.pb')
    _PATH_TO_LABELS = os.path.join('tfmodels', _MODEL_NAME, _LABEL_MAP_NAME)
    
    print("hello world from tagger")
    _load_model()
    print("Successfully loaded model from " + _PATH_TO_FROZEN_GRAPH if _detection_graph else "Failed to load model from" + _PATH_TO_FROZEN_GRAPH)
    _load_labels()
    print("Successfully loaded labels from " + _PATH_TO_LABELS if _detection_graph else "Failed to load labels from" + _PATH_TO_LABELS)
    _load_session()
    print("Successfully initialized TF Session" if _session else "Failed to initializ TF Session")

    # load images and perform detection
    for image_name in TEST_IMAGE_NAMES:
        image = Image.open(os.path.join('test_images', image_name))
        print("Successfully loaded image " + image_name if image else "Failed to load image " + image_name)

        list_of_tags = ', '.join(map(str, detect(image)))
        print('Detection Complete for {}:\n[{}] \n'.format(image_name, list_of_tags))
else:
    # initalization sequence runs upon being imported
    _load_model()
    _load_labels()
    _load_session()
    