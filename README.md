# Photo Tagger - A Django Tensor Flow Project
[![Build Status](https://travis-ci.org/PhotoTagger/django-initial.svg?branch=master)](https://travis-ci.org/PhotoTagger/django-initial) [![Coverage Status](https://coveralls.io/repos/github/PhotoTagger/django-initial/badge.svg?branch=master)](https://coveralls.io/github/PhotoTagger/django-initial?branch=master) [![codecov](https://codecov.io/gh/PhotoTagger/django-initial/branch/master/graph/badge.svg)](https://codecov.io/gh/PhotoTagger/django-initial)

This project is based off of the following tutorial and base template
https://docs.djangoproject.com/en/2.1/intro/tutorial01/

# Setting up your environment

If you don't already have conda, [install conda](https://conda.io/docs/user-guide/install/macos.html)
Take some time to [learn about conda:](https://medium.freecodecamp.org/why-you-need-python-environments-and-how-to-manage-them-with-conda-85f155f4353c)

You can clone this repository, install all dependencies and try it in your
browser quite easily:

```bash
git clone https://github.com/PhotoTagger/django-initial.git
cd django-initial
conda env create -n photoTaggerEnv -f=./environment.yml
source activate photoTaggerEnv
python manage.py migrate
python manage.py runserver
```

To set up your environment, you need to create a one-time environment variable for making requests to cloudinary
For access to one of the keys, please contact an administrator of the repo or create your own account on cloudinary
1. Setup the `CLOUDINARY_URL` environment variable by copying it from the [Management Console](https://cloudinary.com/console):

    Using zsh/bash/sh

        $ export CLOUDINARY_URL=cloudinary://API-Key:API-Secret@Cloud-name

    Using tcsh/csh

        $ setenv CLOUDINARY_URL cloudinary://API-Key:API-Secret@Cloud-name

    Using Windows command prompt/PowerShell

        > set CLOUDINARY_URL=cloudinary://API-Key:API-Secret@Cloud-name

 
# Rules for committing new code
Lets agree on a short list of leading active verbs:
```
add: Create a capability e.g. feature, test, dependency.
delete: Remove a capability e.g. feature, test, dependency.
fix: Fix an issue e.g. bug, typo, accident, misstatement.
build: Change the build process, or tooling, or infra.
refactor: A code change that MUST be just a refactoring.
docs: Refactor of documentation, e.g. help files.
```

Ex: `git commit -m "Add: Added API to urls.py"`


# Useful Conda Commands

Installing dependencies that were added to the environment.yml file
```
conda env update environment.yml
conda activate photoTaggerEnv or source activate photoTaggerEnv
```
Viewing current dependencies installed within an environment
`conda list`

### Sharing dependencies 

Instead of doing a `conda install <package>` 
you should manually add it to the environment.yml file and
then follow the instructions above to perform a conda update

### Testing

Unit tests for a specific module only can be run using this command from the project root /django-initial:
```bash
coverage run --source='.' manage.py test imageprocessor.tagservice
```

This module's tests will also be included automatically as part of overall django test suite by running this command from the project root /django-initial:
```bash
coverage run --source='.' manage.py test
```

You can then view the the code coverage report running this command from the project root /django-initial:
```bash
coverage report -m
```

# API

### /api/classify/
This API accepts one or more images and returns a list of tags for each image.

You can try the API by using this curl command.
```bash
curl -F "file=@[FULL PATH TO IMAGE FILE1]" -F "file=@[FULL PATH TO IMAGE FILE2]" http://127.0.0.1:8000/api/classify/
```

You can also try this API by using the postman app.
1. Set the method to POST
2. Set the url to http://127.0.0.1:8000/api/classify/
3. On the Body tab, select form-data.
4. Set the following:
   * Type "file" in the key field without the quotes.
   * Change the type from text to file.
   * Click the Choose Files button under value and select the image you want to tag.
   * Repeat the previous 3 sub-steps for each image you want to include in your request.
   * Press the Send button

A successful response from this API will have an overall HTTP status code of 207 (Multistatus) and the following JSON structure. Where "results" is an array holding the individual result of each image upload operation.
"status" holds the HTTP status code associated with the individual image
"url" is the location where the image was stored in the cloud and "public_id" is its resource id
"tags" is an array of tags generated for the image.
```JSON
{
    "results": [
        {
            "status": 200,
            "error_message": null,
            "name": "yourimage.jpg",
            "public_id": "yourimage_abcd",
            "url": "http://res.cloudinary.com/yourimage_abcd.jpg",
            "tags": [
                "tagA",
                "tagB",
                "tagC"
            ]
        },
        {
            "status": 415,
            "error_message": "We can't process that file type. Please submit a different file",
            "name": "text_file.txt",
            "public_id": null,
            "url": null,
            "tags": []
        }
    ]
}
```
