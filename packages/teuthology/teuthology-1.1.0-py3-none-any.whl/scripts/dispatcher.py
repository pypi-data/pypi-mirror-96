"""
usage: teuthology-dispatcher --help
       teuthology-dispatcher --supervisor [-v] --bin-path BIN_PATH --job-config COFNFIG --archive-dir DIR
       teuthology-dispatcher [-v] [--archive-dir DIR] --log-dir LOG_DIR --tube TUBE

Start a dispatcher for the specified tube. Grab jobs from a beanstalk
queue and run the teuthology tests they describe as subprocesses. The
subprocess invoked is a teuthology-dispatcher command run in supervisor
mode.

Supervisor mode: Supervise the job run described by its config. Reimage
target machines and invoke teuthology command. Unlock the target machines
at the end of the run.

standard arguments:
  -h, --help                     show this help message and exit
  -v, --verbose                  be more verbose
  -t, --tube TUBE                which beanstalk tube to read jobs from
  -l, --log-dir LOG_DIR          path in which to store logs
  -a DIR, --archive-dir DIR      path to archive results in
  --supervisor                   run dispatcher in job supervisor mode
  --bin-path BIN_PATH            teuthology bin path
  --job-config CONFIG            file descriptor of job's config file
"""

import docopt

import teuthology.dispatcher


def main():
    args = docopt.docopt(__doc__)
    teuthology.dispatcher.main(args)
