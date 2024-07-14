# Run cron jobs within this file as python functions

import os
import shutil
import threading
import time

import schedule

from __init__ import logger
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
    def _task(job_func):
        try:
            job_func()
        except Exception as e:
            logger.error(e)
    
    def run_mon_to_fri_at_time(job_func, at_time):
        schedule.every().monday.at(at_time).do(job_func)
        schedule.every().tuesday.at(at_time).do(job_func)
        schedule.every().wednesday.at(at_time).do(job_func)
        schedule.every().thursday.at(at_time).do(job_func)
        schedule.every().friday.at(at_time).do(job_func)

    _send_report = lambda: _task(send_report)
    _prune_inactive = lambda: _task(prune_inactive)
    
    # TODO: Add a setting to change the time of the day these run
    run_mon_to_fri_at_time(_send_report, "10:00")
    logger.info("Scheduled send_report to run Mon-Fri at 10:00")
    schedule.every().sunday.at("01:00").do(_prune_inactive)
    logger.info("Scheduled prune_inactive to run on Sundays at 01:00")
    schedule.every().sunday.at("01:05").do(_routine_backup)
    logger.info("Scheduled _routine_backup to run on Sundays at 01:05")

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
