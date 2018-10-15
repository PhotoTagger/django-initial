# Tag Service

This module is an object detector built on top of the [TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection)

## Proposed Usage

The tagger module has one function called `detect` that is intended to be imported and used like this:
```python
from imageprocessor.tagservice.tagger import detect

# perform detection and return a list of tags
tags = detect(image)
```

If we add more functions to tagger besides just `detect` in the future, then it may be better to import it like this
```python
from imageprocessor.tagservice import tagger

# perform detection and return a list of tags
tags = tagger.detect(image)
```

### Testing

Unit tests for this module only can be run using this command from the project root /django-initial:
```bash
python manage.py test imageprocessor.tagservice
```

This module's tests will also be included automatically as part of overally django test suite by running this command from the project root /django-initial:
```bash
python manage.py test
```

## Folder structure:
* tagger.py - the main script to be imported. It has 1 public method called detect()
* test.py - unit tests for tagger go here
* tfutils - holds utility scripts from the TF Object Detection API
* tfmodels - holds pretrained models downloaded from the [tf model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md)
* test_images - hold test images =p
