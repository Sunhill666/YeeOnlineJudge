from celery import shared_task

from submission.models import Submission
from utils.judger import submission
from utils.tools import read_test_case, do_before


@shared_task
def to_judge(code, language_id, problem, submission_id, training=None):
    submit = Submission.objects.get(pk=submission_id)
    submit.status = Submission.Status.PROCESSING
    submit.save()

    test_case = problem.test_case.file
    stdin_list, expected_output_list = read_test_case(test_case)
    token_list = list()
    wrong_flag = False
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
        if sub.status.get('id') > 3:
            wrong_flag = True
            submit.status = Submission.translate_status(sub.status)
            if problem.mode == 'ACM':
                break

        if problem.mode == 'OI' and (not wrong_flag):
            submit.status = Submission.translate_status(sub.status)

    submit.token = token_list
    submit.save()

    if training:
        process_training.delay(submission_id)
    else:
        process_statistics.delay(submission_id, "Problem")
        process_statistics.delay(submission_id, "User")


@shared_task
def process_statistics(submission_id, process_type):
    submit = Submission.objects.get(pk=submission_id)
    creator_profile = submit.created_by.profile
    problem = submit.problem

    if process_type == "User":
        statistics = creator_profile.statistics
    else:
        statistics = problem.statistics

    statistics.update(commit=statistics.get('commit', 0) + 1)

    if not do_before(creator_profile.user_id, problem.id, submit.status):
        if submit.status == Submission.Status.ACCEPTED:
            statistics.update(accepted=statistics.get('accepted', 0) + 1)
        elif submit.status == Submission.Status.WA:
            statistics.update(wa=statistics.get('wa', 0) + 1)
        elif submit.status == Submission.Status.TLE:
            statistics.update(tle=statistics.get('tle', 0) + 1)
        elif submit.status == Submission.Status.CE:
            statistics.update(commit=statistics.get('ce', 0) + 1)
        elif submit.status == Submission.Status.RE:
            statistics.update(commit=statistics.get('re', 0) + 1)
        elif submit.status == Submission.Status.IE:
            statistics.update(commit=statistics.get('ie', 0) + 1)
        elif submit.status == Submission.Status.EFE:
            statistics.update(commit=statistics.get('efe', 0) + 1)

    if process_type == "User":
        creator_profile.statistics = statistics
        creator_profile.save()
    else:
        problem.statistics = statistics
        problem.save()


@shared_task
def process_training(submission_id):
    submit = Submission.objects.get(pk=submission_id)
    train = submit.training
    tokens = submit.token
    right_before = False
