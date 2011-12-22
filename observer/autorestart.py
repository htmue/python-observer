# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   autorestart.py --- Restart program on file change
#=============================================================================
import logging
import os
import re
import signal
import subprocess
import threading

from observer.tree import TreeObserver


try:
    from growler import Notifier
except ImportError:
    growler = None
else:
    growler = Notifier()


log = logging.getLogger(__name__)

DEFAULT_FILEPATTERN = re.compile(r'.*\.(py|txt|yaml|sql|html|js|css)$')

class AutorestartObserver(TreeObserver):
    
    def __init__(self, dir, args, filepattern=DEFAULT_FILEPATTERN):
        self._lock = threading.Lock()
        self.child = None
        self.args = args
        super(AutorestartObserver, self).__init__(dir, filepattern, ignored_dirs_pattern(dir))
    
    @property
    def child(self):
        with self._lock:
            return self._child
    
    @child.setter
    def child(self, child):
        with self._lock:
            self._child = child
    
    def kill_child(self):
        child = self.child
        if child is not None:
            child.send_signal(signal.SIGINT)
            child.wait()
            child = None
    
    def restart_child(self):
        self.kill_child()
        self.child = subprocess.Popen(self.args, close_fds=True)
    
    def action(self, entries):
        restarted = self.child is not None
        self.restart_child()
        if growler is not None:
            growler.notify(
                '{}started: {}'.format('re' if restarted else '',
                ' '.join(self.args)), 'in {}'.format(os.getcwd()),
            )


def ignored_dirs_pattern(dir):
    dirs = list(ignored_dirs(dir))
    if dirs:
        pattern = r'(%s)$' % '|'.join(dirs)
        log.debug('ignored_dirs_pattern: %s', pattern)
        return re.compile(pattern)

def ignored_dirs(dir):
    git_exclude = os.path.join(dir, '.git', 'info', 'exclude')
    git_ignore = os.path.join(dir, '.gitignore')
    for name in (git_exclude, git_ignore):
        for ignore in ignored_dirs_from_file(dir, name):
            log.debug('ignored_dirs:%s:%s', name, ignore)
            yield ignore

def ignored_dirs_from_file(dir, name):
    dir_re = re.compile(r'/([^/]+)/?$')
    if os.path.exists(name):
        for line in open(name):
            match = dir_re.match(line.strip())
            if match:
                ignore = os.path.join(dir, match.group(1))
                if os.path.isdir(ignore):
                    yield ignore

#.............................................................................
#   autorestart.py
