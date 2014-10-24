import sys
import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


class WatcherError(Exception):
    pass


class RestartProcessHandler(LoggingEventHandler):
    def __init__(self, proc_name, *args, **kwargs):
        self.proc_name = proc_name
        self.delta = kwargs.get('delta', 5)
        self.last_reacted = 0
        self.start_process()
        super(RestartProcessHandler, self).__init__(*args, **kwargs)

    def kill_process(self):
        proc = subprocess.Popen(['pgrep', self.proc_name],
                                stdout=subprocess.PIPE)
        out, err = proc.communicate()
        pids = [int(x) for x in out.strip().split('\n')] if out != '' else []
        # kill other instances
        for pid in pids:
            os.kill(pid, 9)

    def start_process(self):
        xterm = ['xterm', '-e']
        command = [x.strip() for x in self.proc_name.split(' ')]
        xterm.extend(command)
        subprocess.Popen(xterm)
        self.last_reacted = time.time()

    def on_created(self, event):
        super(RestartProcessHandler, self).on_created(event)
        self._process_event()

    def on_modified(self, event):
        super(RestartProcessHandler, self).on_modified(event)
        self._process_event()

    def _process_event(self):
        if time.time() - self.last_reacted < self.delta:
            return
        self.kill_process()
        self.start_process()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %h:%M:%S%')
    if len(sys.argv) < 2:
        raise WatcherError("Path to directory should come as first param")
    process_name = "glance-api" if len(sys.argv) == 2 else sys.argv[2]
    path = sys.argv[1]
    event_handler = RestartProcessHandler(process_name)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        event_handler.kill_process()
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
