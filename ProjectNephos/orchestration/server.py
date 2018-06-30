from ProjectNephos.orchestration.tasks import add_task

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from logging import getLogger

logger = getLogger(__name__)


class Server(object):
    """
    This is the main background Orchestration class. This will run every REFRESH_TIMER
    seconds and perform tasks. Each task is assumed to follow these guidelines:
        * Available in the JOB_LIST variable.
        * Independent from any other function in the list.
        * Takes config as the only argument (as of now).
        * Raises anything when it fails.
        * Raises nothing for a successful run.

    In case the task fails, it logs appropriately. No mechanism (as yet) has been provided to
    log errors from scheduler side. That task lies with the task, itself.

    The core of this server is a scheduler(APScheduler). It makes sure that jobs(functions)
    run at the specified REFRESH_TIMER. Event listeners are put in place to react to failures/successes.
    """
    JOB_LIST = [add_task]
    REFRESH_TIMER = 5

    def __init__(self, config):
        self.config = config
        self.jobs = self.JOB_LIST
        self.running_jobs = []
        logger.debug("Starting Orchestration.")

        self.sched = BlockingScheduler(
            jobstore=MemoryJobStore(),
            executor=ProcessPoolExecutor(5),
            job_defaults={
                "coalesce": True,  # Combine multiple waiting instances of the same job into one.
                "max_instances": 2,  # Total number of concurrent instances for the sam job. Change to 1 for upload.
            },
        )

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
        for item in self.jobs:
            j = self.sched.add_job(
                item, args=[self.config], trigger="interval", seconds=self.REFRESH_TIMER
            )
            logger.critical("Added job {}: {}".format(j.id, j.func))

        self.sched.add_listener(
            self.endjob_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED
        )

        try:
            self.sched.start()
        except KeyboardInterrupt:
            logger.info("Interrupt recieved.")
            self.sched.shutdown()
            logger.debug("Orchestration shut down.")
