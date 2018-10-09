# Tag Service

This module is an object detector built on top of the TensorFlow Object Detection API:
https://github.com/tensorflow/models/tree/master/research/object_detection

To try this module run the command line from django-initial\imageprocessor\tagservice
```bash
python tagger.py
```

The tagger module is intended to be imported and used like this:
```python
from tagservice import tagger

# perform detection and return a list of tags
tags = tagger.detect(image)
```

Folder structure:
* tagger.py - the main script to be imported. It has 1 public method called detect()
* label_map_utils.py and string_int_label_map_pb2.py are utilities from the object detection api project
* tfmodels - holds pretrained models downloaded from the model zoo https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
* test_images - hold test images =p
