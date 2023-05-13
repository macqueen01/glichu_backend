
from celery import result


def task_status(task_id):

    # PENDING --> 4
    # RUNNING --> 3
    # FAILURE --> 0
    # SUCCESS --> 1
    # TASK NOT FOUND --> 2

    if not task_id:
        return 2

    task = result.AsyncResult(task_id)

    if task.state == 'FAILURE':
        return 0

    elif task.state == 'RUNNING':
        return 3

    elif task.state == 'PENDING':
        return 4

    elif task.state == 'SUCCESS':
        return 1

    return 2


def get_result_from_task_id(task_id):

    if task_status(task_id) != 1:
        return False

    return result.AsyncResult(task_id).result

