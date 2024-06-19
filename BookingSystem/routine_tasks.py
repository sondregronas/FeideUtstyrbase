# Run cron jobs within this file as python functions

import os
import shutil
import threading
import time

import schedule

from db import DATABASE
from teams import send_report
from user import prune_inactive


def _routine_backup():
    # Filename = backup-<year>-w<week>.sqlite
    filename = time.strftime('backup-%Y-w%W.sqlite')

    if not os.path.exists('data/backups'):
        os.mkdir('data/backups')

    shutil.copyfile(DATABASE, f'data/backups/{filename}')


def start_routine():
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    def run_mon_to_fri_at_time(job_func, at_time):
        schedule.every().monday.at(at_time).do(run_threaded, job_func)
        schedule.every().tuesday.at(at_time).do(run_threaded, job_func)
        schedule.every().wednesday.at(at_time).do(run_threaded, job_func)
        schedule.every().thursday.at(at_time).do(run_threaded, job_func)
        schedule.every().friday.at(at_time).do(run_threaded, job_func)

    # TODO: Add a setting to change the time of the day these run
    run_mon_to_fri_at_time(send_report, "10:00")
    schedule.every().sunday.at("01:00").do(run_threaded, prune_inactive)
    schedule.every().sunday.at("01:05").do(run_threaded, _routine_backup)

    while True:
        schedule.run_pending()
        time.sleep(1)
