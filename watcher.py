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
        super(RestartProcessHandler, self).__init__(*args, **kwargs)

    def kill_processes(self):
        proc = subprocess.Popen(['pgrep', 'xterm'],
                                stdout=subprocess.PIPE)
        out, err = proc.communicate()
        pids = [int(x) for x in out.strip().split('\n')] if out != '' else []
        # kill other instances
        for pid in pids:
            os.kill(pid, 9)

    def on_any_event(self, event):
        self.kill_processes()
        # restart glance (watcher script should be run in same VENV where glance
        # is mind that!)
        xterm = ['xterm', '-e']
        command = [x.strip() for x in self.proc_name.split(' ')]
        xterm.extend(command)
        subprocess.Popen(xterm)


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
        event_handler.kill_processes()
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
