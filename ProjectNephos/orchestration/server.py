from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from ProjectNephos.orchestration.tasks import run_job

# from ProjectNephos.orchestration.recording import record_video
from ProjectNephos.backends import DBStorage

from multiprocessing import Process
from logging import getLogger
from xmlrpc.server import SimpleXMLRPCServer

logger = getLogger(__name__)
scheduler = None  # The actual scheduler that is to be manipulated later
configuration = None  # Configuration
rpc_server = None


def record_video(job, config):
    logger.critical(job)


class Server(object):
    """
    This is the main background Orchestration class. This will run every REFRESH_TIMER
    seconds and perform tasks. Each task is assumed to follow these guidelines:
        * Available in the JOB_LIST variable or is an recording job.
        * Independent from any other function in the list.
        * Takes the scheduler and config as the only argument (as of now).
        * Raises anything when it fails.
        * Raises nothing for a successful run.

    In case the task fails, it logs appropriately. No mechanism (as yet) has been provided to
    log errors from scheduler side. That task lies with the task, itself.

    The core of this server is a scheduler(APScheduler). It makes sure that jobs(functions)
    run at the specified REFRESH_TIMER. Event listeners are put in place to react to failures/successes.
    """
    JOB_LIST = [run_job]
    REFRESH_TIMER = 5

    def __init__(self, config):
        self.config = config
        self.db = DBStorage(config)

        self.jobs = self.JOB_LIST
        self.running_jobs = []
        logger.debug("Starting Orchestration.")

        self.sched = BackgroundScheduler(
            jobstore=MemoryJobStore(),
            executor=ProcessPoolExecutor(5),
            job_defaults={
                "coalesce": True,  # Combine multiple waiting instances of the same job into one.
                "max_instances": 9,  # Total number of concurrent instances for the same job.
            },
        )

        self.rpc = SimpleXMLRPCServer(("localhost", 8080))

    def setup_rpc_server(self):
        self.rpc.register_function(add_job_rpc, "add_job")
        self.rpc.register_function(close)

    def add_regular_jobs(self):
        for item in self.jobs:
            j = self.sched.add_job(
                item,
                args=[self.sched, self.config],
                trigger="interval",
                seconds=self.REFRESH_TIMER,
            )
            logger.debug("Added regular job {}: {}".format(j.id, j.func))

    def add_recording_jobs(self):
        job_list = self.db.get_job()

        for job in job_list:
            cron = job.start.split()

            j = self.sched.add_job(
                record_video,
                args=[job, self.config],
                trigger="cron",
                minute=cron[0],
                hour=cron[1],
                day=cron[2],
                month=cron[3],
                day_of_week=cron[4],
                year=cron[5],
            )
            logger.debug("Added recording job {}: {}".format(j.id, j.func))

    @staticmethod
    def endjob_listener(event):
        if event.exception:
            logger.critical("Job {}: FAILED".format(event.job_id))
        else:
            logger.critical(
                "Job {}: SUCCEEDED with return value {}".format(
                    event.job_id, event.retval
                )
            )

    def run_server(self):
        self.add_regular_jobs()
        self.add_recording_jobs()

        self.sched.add_listener(
            self.endjob_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED
        )

        self.db.session.close()
        self.sched.start()

        global scheduler, configuration, rpc_server
        scheduler = self.sched
        configuration = self.config
        rpc_server = self.rpc

        self.setup_rpc_server()
        self.rpc.serve_forever()


def add_job_rpc(name):
    global configuration
    db = DBStorage(configuration)

    job = db.get_job(jobname=name)

    cron = job.start.split()
    global scheduler
    j = scheduler.add_job(
        record_video,
        args=[job, configuration],
        trigger="cron",
        minute=cron[0],
        hour=cron[1],
        day=cron[2],
        month=cron[3],
        day_of_week=cron[4],
        year=cron[5],
    )
    logger.debug("Added recording job {}: {}".format(j.id, j.func))
    db.session.close()
    return True


def close():
    global scheduler, rpc_server
    scheduler.shutdown()
    rpc_server.server_close()
    return True
