observer
========

Observe files and directories for changes. Act on file creation, deletion and content changes.

Uses [inotifyx](https://launchpad.net/inotifyx) on Linux and [py-kqueue](http://pypi.python.org/pypi/py-kqueue/2.0.1) on Mac OSX.


Example
-------

Run program and restart it on file changes in the directory tree:

    $ autorestart program args

Print Python source code changes to stdout:

```python
import pprint
import re

from observer.gitignore import GitIgnore
from observer.tree import TreeObserver


class ChangesLogger(TreeObserver):

    def __init__(self, basedir='.'):
        super(ChangesLogger, self).__init__(basedir, re.compile(r'.*\.py$'), GitIgnore(basedir))

    def action(self, entries):
        print pprint.pformat(sorted(entries))

ChangesLogger().loop()
```


Installation
------------

    $ pip install -e git+https://github.com/htmue/python-observer#egg=observer

On Mac OSX, install py-kqueue:

    $ pip install py-kqueue==2.0.1

And optionally, for Growl support in ```autorestart```:

    $ pip install gntp==0.5.1

On Linux:

    $ pip install inotifyx==0.2.0


Tests
-----

In source directory:

    $ python -m doctest README.md

Setup:

    >>> from observer import Observer

    >>> import tempfile, shutil, os
    >>> dir = tempfile.mkdtemp()

Watch for directory creation/deletion:

    >>> o = Observer(dir, '*', dirs=True)
    >>> o.changes()
    ([], [], [])
    >>> os.mkdir(os.path.join(dir, 'test1'))
    >>> created, changed, deleted = o.changes()
    >>> len(created)
    1
    >>> len(deleted)
    0
    >>> created
    ['test1']

    >>> os.mkdir(os.path.join(dir, 'test2'))
    >>> created, changed, deleted = o.changes()
    >>> len(created)
    1
    >>> len(deleted)
    0
    >>> created
    ['test2']

    >>> os.mkdir(os.path.join(dir, 'test31'))
    >>> os.mkdir(os.path.join(dir, 'test32'))
    >>> created, changed, deleted = o.changes()
    >>> len(created)
    2
    >>> len(deleted)
    0
    >>> created
    ['test31', 'test32']

    >>> shutil.rmtree(os.path.join(dir, created[1]))
    >>> created, changed, deleted = o.changes()
    >>> len(created)
    0
    >>> len(deleted)
    1
    >>> deleted
    ['test32']

Watch for file creation:

    >>> filename = 'entries'
    >>> o = Observer(dir, filename)
    >>> o.changes()
    ([], [], [])
    >>> open(os.path.join(dir, filename), 'w').close()
    >>> created, changed, deleted = o.changes()
    >>> len(created)
    1
    >>> len(deleted)
    0
    >>> created[0] == filename
    True

Teardown:

    >>> shutil.rmtree(dir)


TODO
----

* make ```autorestart``` file pattern configurable
* handle logging config
* more tests

Contributions are welcome!


License
-------

This is free and unencumbered software released into the public domain.

see [UNLICENSE](http://unlicense.org/)
