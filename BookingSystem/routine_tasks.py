# Run cron jobs within this file as python functions

import json
import os
import shutil
import threading
import time
from datetime import datetime

import schedule

from __init__ import logger
from db import DATABASE, Settings
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
    def update_db(fn_name):
        data = json.loads(Settings.get('routine_tasks') or '{}')
        if not data.get(fn_name):
            data[fn_name] = dict({'last_run': None, 'runs': 0})

        data[fn_name]['last_run'] = datetime.now().timestamp()
        data[fn_name]['runs'] += 1

        Settings.set('routine_tasks', json.dumps(data))

    def _task(job_func, job_name=''):
        try:
            job_func()
            update_db(job_name)
        except Exception as e:
            logger.error(e)

    def run_mon_to_fri_at_time(job_func, at_time):
        func_name = job_func.__name__
        job_func.__name__ = f'{func_name} (Mandag)'
        schedule.every().monday.at(at_time).do(job_func)
        job_func.__name__ = f'{func_name} (Tirsdag)'
        schedule.every().tuesday.at(at_time).do(job_func)
        job_func.__name__ = f'{func_name} (Onsdag)'
        schedule.every().wednesday.at(at_time).do(job_func)
        job_func.__name__ = f'{func_name} (Torsdag)'
        schedule.every().thursday.at(at_time).do(job_func)
        job_func.__name__ = f'{func_name} (Fredag)'
        schedule.every().friday.at(at_time).do(job_func)

    __routine_backup = lambda: _task(_routine_backup, 'Ukentlig backup')
    __send_report = lambda: _task(send_report, 'Send Dagsrapport')
    __prune_inactive = lambda: _task(prune_inactive, 'Rydd opp brukere')
    __routine_backup.__name__ = 'Ukentlig backup'  # Set name for scheduler
    __send_report.__name__ = 'Send Dagsrapport'  # Set name for scheduler
    __prune_inactive.__name__ = 'Rydd opp brukere'  # Set name for scheduler

    # TODO: Add a setting to change the time of the day these run from frontend
    run_mon_to_fri_at_time(__send_report, "10:00")
    logger.info("Scheduled send_report to run Mon-Fri at 10:00")
    schedule.every().sunday.at("01:00").do(__prune_inactive)
    logger.info("Scheduled prune_inactive to run on Sundays at 01:00")
    schedule.every().sunday.at("01:05").do(__routine_backup)
    logger.info("Scheduled _routine_backup to run on Sundays at 01:05")

    # Run the schedule
    return run_continuously()


def threaded_start_routine(main_pid: int) -> None:
    # NOTE: This (nested threads) shouldn't be necessary, but I could not get the atexit.register to work properly
    # with the main gunicorn process. This is a workaround to ensure that the routine tasks are stopped when the main
    # process exits.
    import atexit

    t = threading.Thread(target=start_routine, args=(), daemon=True)
    t.start()

    @atexit.register
    def cleanup():
        # Cleanup on exit
        logger.info(f"Cleaning up {os.getpid()}... (Parent PID: {main_pid})")
        if main_pid == os.getpid():
            # Exit routine tasks process (only if main process is exiting)
            t.join()
            logger.info("Stopping routine tasks...")
        else:
            # Exit child processes
            logger.info(f"Exiting child process with PID {os.getpid()}")
            os._exit(0)  # Exit without calling cleanup
