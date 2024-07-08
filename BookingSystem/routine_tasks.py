# Run cron jobs within this file as python functions

import os
import shutil
import threading
import time

import schedule

from db import DATABASE
from teams import send_report
from user import prune_inactive


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def _routine_backup():
    # Filename = backup-<year>-w<week>.sqlite
    filename = time.strftime('backup-%Y-w%W.sqlite')

    if not os.path.exists('data/backups'):
        os.mkdir('data/backups')

    shutil.copyfile(DATABASE, f'data/backups/{filename}')


def start_routine():
    def run_mon_to_fri_at_time(job_func, at_time):
        schedule.every().monday.at(at_time).do(job_func)
        schedule.every().tuesday.at(at_time).do(job_func)
        schedule.every().wednesday.at(at_time).do(job_func)
        schedule.every().thursday.at(at_time).do(job_func)
        schedule.every().friday.at(at_time).do(job_func)

    # TODO: Add a setting to change the time of the day these run
    run_mon_to_fri_at_time(send_report, "10:00")
    schedule.every().sunday.at("01:00").do(prune_inactive)
    schedule.every().sunday.at("01:05").do(_routine_backup)

    # Run the schedule
    return run_continuously()


def get_job_status():
    return {
        'jobs': {
            job.job_func.__name__: {'last_run': job.last_run.isoformat() if job.last_run else '',
                                    'next_run': job.next_run.isoformat(),
                                    'last_run_dt': job.last_run,
                                    'next_run_dt': job.next_run}
            for job in schedule.get_jobs()}
    }
