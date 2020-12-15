from abc import ABCMeta, abstractmethod
from decimal import Decimal

from celery.result import AsyncResult, allow_join_result

from .models import ProgressPersistent


PROGRESS_STATE = 'PROGRESS'


class AbstractProgressRecorder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total, description=""):
        pass

    @abstractmethod
    def stop_task(self, current, total, exc):
        pass


class ConsoleProgressRecorder(AbstractProgressRecorder):

    def set_progress(self, current, total, description=""):
        print('processed {} items of {}. {}'.format(current, total, description))


    def stop_task(self, current, total, exc):
        pass


class ProgressRecorder(AbstractProgressRecorder):

    def __init__(self, task):
        self.task = task

    def set_progress(self, current, total, description=""):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        self.task.update_state(
            state=PROGRESS_STATE,
            meta={
                'pending': False,
                'current': current,
                'total': total,
                'percent': percent,
                'description': description
            }
        )

    def stop_task(self, current, total, exc):
        self.task.update_state(
            state='FAILURE',
            meta={
                'pending': False,
                'current': current,
                'total': total,
                'percent': 100.0,
                'exc_message': str(exc),
                'exc_type': str(type(exc))
            }
        )

class ProgressPersistentRecorder(ProgressRecorder):
    def __init__(self, task, user):
        super().__init__(task)
        ProgressPersistent.objects.create(task_id=task.request.id, completed=False, user=user)

    def set_progress(self, current, total, description=""):
        super().set_progress(current, total, description)

    def stop_task(self, current, total, exc):
        super().stop_task(current, total, exc)


class Progress(object):

    def __init__(self, task_id):
        self.task_id = task_id
        self.result = AsyncResult(task_id)

    def get_info(self):
        if self.result.ready():
            success = self.result.successful()
            with allow_join_result():
                return {
                    'complete': True,
                    'success': success,
                    'progress': _get_completed_progress(),
                    'result': self.result.get(self.task_id) if success else str(self.result.info),
                }
        elif self.result.state == PROGRESS_STATE:
            return {
                'complete': False,
                'success': None,
                'progress': self.result.info,
            }
        elif self.result.state in ['PENDING', 'STARTED']:
            return {
                'complete': False,
                'success': None,
                'progress': _get_unknown_progress(self.result.state),
            }
        return self.result.info


def _get_completed_progress():
    return {
        'pending': False,
        'current': 100,
        'total': 100,
        'percent': 100,
    }


def _get_unknown_progress(state):
    return {
        'pending': state == 'PENDING',
        'current': 0,
        'total': 100,
        'percent': 0,
    }
