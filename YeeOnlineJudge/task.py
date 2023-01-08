from celery import shared_task

from submission.models import Submission
from utils.judger import submission
from utils.tools import read_test_case


@shared_task
def process_training(submission_id):
    submit = Submission.objects.get(pk=submission_id)
    tokens = submit.token
    right_before = False


@shared_task
def to_judge(code, language_id, problem, submission_id, training=None):
    submit = Submission.objects.get(pk=submission_id)
    submit.status = Submission.Status.PROCESSING
    submit.save()

    test_case = problem.test_case.file
    stdin_list, expected_output_list = read_test_case(test_case)
    token_list = list()
    for stdin, expected_output in zip(stdin_list, expected_output_list):
        sub = submission.submit(
            source_code=bytes(code, 'utf-8'),
            language=language_id,
            stdin=bytes(stdin, 'utf-8'),
            expected_output=None if not expected_output else bytes(expected_output, 'utf-8'),
            cpu_time_limit=problem.time_limit / 1000,
            memory_limit=problem.memory_limit * 1024,
            wait=True
        )
        token_list.append(sub.token)
        submit.status = Submission.translate_status(sub.status)
        if sub.status.get('id') > 3 and problem.mode == 'ACM':
            break
    submit.token = token_list
    submit.save()

    if training:
        process_training.delay(submission_id)
    else:
        process_problem.delay(submission_id)
        process_profile.delay(submission_id)


@shared_task
def process_profile(submission_id):
    pass


@shared_task
def process_problem(submission_id):
    pass
