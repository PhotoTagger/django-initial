# Photo Tagger - A Django Tensor Flow Project

This project is based off of the following tutorial and base template
https://docs.djangoproject.com/en/2.1/intro/tutorial01/

# Prerequisite requirements

First, before following the setup instructions, install conda on your machine
Instructions: https://conda.io/docs/user-guide/install/macos.html
Why you need conda: https://medium.freecodecamp.org/why-you-need-python-environments-and-how-to-manage-them-with-conda-85f155f4353c

You can clone this repository, install all dependencies and try it in your
browser quite easily:

```bash
git clone https://github.com/PhotoTagger/django-initial.git
cd django-initial
conda env create -n photoTaggerEnv -f=./environment.yml
source activate photoTaggerEnv
python manage.py runserver
```

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
