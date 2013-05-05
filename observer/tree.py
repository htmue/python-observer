# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   tree.py --- Tree observer
#=============================================================================
import os
import threading
from Queue import Queue

from logger import Logger
from observer import Observer


class DirObserver(Observer):

    def __init__(self, dir, filepattern, ignore, queue):
        self.observers = dict()
        self.filepattern = filepattern
        self.ignore = ignore
        self.queue = queue
        super(DirObserver, self).__init__(dir, '*', changes=True)
        self.add_observer(self)

    def __del__(self):
        for observer in self.observers.values():
            self.remove_observer(observer)

    def isdir(self, entry):
        return os.path.isdir(os.path.join(self.dir, entry))

    def check_entry(self, entry):
        if os.path.isdir(entry):
            return True if self.ignore is None else not self.ignore(entry)
        else:
            return self.filepattern.match(entry)

    def enqueue(self, entry):
        self.queue.put(os.path.join(self.dir, entry))

    def on_create(self, entry):
        self.log.debug('%s.on_create: "%s"', self, entry)
        if self.isdir(entry):
            self.log.debug('adding observer: %s', entry)
            observer = DirObserver(os.path.join(self.dir, entry), self.filepattern, self.ignore, self.queue)
            self.observers[entry] = observer
        else:
            self.enqueue(entry)

    def on_change(self, entry):
        self.log.debug('%s.on_change: "%s"', self, entry)
        if not self.isdir(entry):
            self.enqueue(entry)

    def on_delete(self, entry):
        self.log.debug('%s.on_delete: "%s"', self, entry)
        if self.isdir(entry):
            if entry in self.observers:
                self.remove_observer(self.observers.pop(entry))
        else:
            self.enqueue(entry)


class TreeObserver(threading.Thread, Logger):
    
    def __init__(self, basedir, filepattern, ignore):
        super(TreeObserver, self).__init__()
        self.queue = Queue()
        self.root = DirObserver(basedir, filepattern, ignore, self.queue)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            entries = [self.queue.get()]
            while not self.queue.empty():
                entries.append(self.queue.get_nowait())
            self.log.debug('entries %s', entries)
            self.action(entries)

    def loop(self, interval=1):
        self.root.loop(interval)

    def action(self, entries):
        self.log.warn('TreeObserver:action: not implemented')


#.............................................................................
#   tree.py
