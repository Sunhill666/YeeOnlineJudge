from celery import shared_task
from django.db.models import Q

from problem.models import Problem
from submission.models import Submission
from utils.judger import submission
from utils.tools import read_test_case, do_before


@shared_task
def to_judge(code, language_id, problem_id, submission_id, training=None):
    submit = Submission.objects.get(pk=submission_id)
    submit.status = Submission.Status.PROCESSING
    submit.save()

    problem = Problem.objects.get(pk=problem_id)

    test_case = problem.test_case.file
    stdin_list, expected_output_list = read_test_case(test_case)
    token_list = list()
    wrong_flag = False
    # 将一道题目中的每个测试样例和提交的代码送去判题机
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
        # 题目的状态id大于3即为出错，对于ACM模式直接停止判题并记录提交状态。对于OI模式则继续，但不会继续更新此提交的状态
        if sub.status.get('id') > 3:
            wrong_flag = True
        if problem.mode == 'ACM':
            submit.status = Submission.translate_status(sub.status)
            if wrong_flag:
                break
        if problem.mode == 'OI' and (not wrong_flag):
            submit.status = Submission.translate_status(sub.status)

    submit.token = token_list
    submit.save()

    if training:
        pass
    else:
        process_statistics.delay(submission_id, "Problem")
        process_statistics.delay(submission_id, "User")
    return submit.id, submit.status


@shared_task
def process_statistics(submission_id, process_type):
    submit = Submission.objects.get(pk=submission_id)
    creator_profile = submit.created_by.profile
    problem = submit.problem

    # 更新题目或用户数据
    if process_type == "User":
        statistics = creator_profile.statistics
        statistics.update(Commit=Submission.objects.filter(
            Q(problem_id=problem.id) & Q(created_by=creator_profile.user_id)
        ).count())
        if not do_before(creator_profile.user_id, problem.id, submit.status):
            statistics.update({
                submit.status: Submission.objects.filter(
                    Q(problem_id=problem.id) &
                    Q(status=submit.status) &
                    Q(created_by=creator_profile.user_id)
                ).distinct().count()
            })
            creator_profile.statistics = statistics
            creator_profile.save()
    else:
        statistics = problem.statistics
        statistics.update(Commit=Submission.objects.filter(problem_id=problem.id).count())
        if not do_before(creator_profile.user_id, problem.id, submit.status):
            statistics.update({
                submit.status: Submission.objects.filter(
                    Q(problem_id=problem.id) &
                    Q(status=submit.status)
                ).distinct().count()
            })
            problem.statistics = statistics
            problem.save()
    return {process_type: statistics}


# @shared_task
# def process_training(submission_id):
#     submit = Submission.objects.get(pk=submission_id)
#     train = submit.training
#     tokens = submit.token
#     right_before = False
