# Plugin.video.animepie

Unofficial kodi addon to play videos from [animepie](http://animepie.to)

# Installing for local development

In order to run the unit tests you will need to install the python libraries in the requirements.txt file

```shell
pip install -r requirements.txt
```

NOTE: For unit tests we are installing js2py. When running on kodi it is going to be using the version
from my repository. Need to ensure that those two stay in sync with each other

# Running unit tests

To actually run the tests we will use pytest

```
pytest -v
```

If you want to view test coverage then you can use the pytest-cov package

```shell
pytest --cov=resources.lib tests/
```
