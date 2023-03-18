from time import sleep

from celery import shared_task
from django.db.models import Q

from problem.models import Problem
from submission.models import Submission
from utils.judger import submission
from utils.tools import read_test_case


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
    if training:
        train = submit.training
        user = submit.created_by
        statistics = train.trainingrank_set.get(user=user).statistics
        test_case_status = statistics.get(str(problem_id), {})
    else:
        statistics = {}
        test_case_status = {}
    # 将一道题目中的每个测试样例和提交的代码送去判题机
    for index, val in enumerate(zip(stdin_list, expected_output_list)):
        stdin = val[0]
        expected_output = val[1]
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
        index = str(index)
        if problem.mode == 'OI' and (not wrong_flag):
            submit.status = Submission.translate_status(sub.status)

        # 提交的状态id大于3即为出错，对于ACM模式直接停止判题并记录提交状态。对于OI模式则继续，但不会继续更新此提交的状态
        if sub.status.get('id') > 3:
            # 之前做对不更新
            if not test_case_status.get(index):
                test_case_status.update({index: False})
            wrong_flag = True
        elif sub.status.get('id') == 3:
            test_case_status.update({index: True})
        else:
            if not test_case_status.get(index):
                test_case_status.update({index: None})

        if problem.mode == 'ACM':
            submit.status = Submission.translate_status(sub.status)
            if wrong_flag:
                break

    submit.token = token_list
    submit.save()

    statistics.update({str(problem_id): test_case_status})

    if training:
        work = process_training.delay(submission_id, statistics)
        # 等待排名更新操作完成
        while not work.ready():
            sleep(0.1)
        process_statistics.delay(submission_id, "Training", training)
    else:
        process_statistics.delay(submission_id, "Problem")
        process_statistics.delay(submission_id, "User")
    return submit.id, submit.status, statistics


@shared_task
def process_statistics(submission_id, process_type, training=None):
    submit = Submission.objects.get(pk=submission_id)
    creator_profile = submit.created_by.profile
    problem = submit.problem

    # 更新题目或用户数据
    if process_type == "User":
        statistics = creator_profile.statistics
        statistics.update(Commit=Submission.objects.filter(created_by=creator_profile.user_id).count())
        statistics.update({
            submit.status: Submission.objects.filter(
                Q(status=submit.status) &
                Q(created_by=creator_profile.user_id)
            ).distinct("problem").count()
        })
        creator_profile.statistics = statistics
        creator_profile.save()
    elif process_type == "Problem":
        statistics = problem.statistics
        statistics.update(Commit=Submission.objects.filter(problem_id=problem.id).count())
        statistics.update({
            submit.status: Submission.objects.filter(
                Q(problem_id=problem.id) &
                Q(status=submit.status)
            ).distinct("created_by").count()
        })
        problem.statistics = statistics
        problem.save()
    elif process_type == "Training":
        train = submit.training
        train_rank = train.trainingrank_set.get(user=submit.created_by)
        statistics = train_rank.statistics.get("statistics")
        statistics.update(Commit=Submission.objects.
                          filter(Q(created_by=submit.created_by) & Q(training=training)).count())
        statistics.update({
            submit.status: Submission.objects.filter(
                Q(training=training) &
                Q(status=submit.status)
            ).distinct("problem").count()
        })
        train_rank.statistics.update(statistics=statistics)
        train_rank.save()
    else:
        return "process_type 有误"
    return {process_type: statistics}


@shared_task
def process_training(submission_id, new_statistics):
    submit = Submission.objects.get(pk=submission_id)
    user = submit.created_by
    train = submit.training
    train_rank = train.trainingrank_set.get(user=user)
    old_statistics = train_rank.statistics
    old_statistics.update(new_statistics)
    score = 0
    # 计算分数
    for key, val in old_statistics.items():
        if key == "score" or key == "statistics":
            continue
        problem = Problem.objects.get(pk=int(key))
        point = problem.point
        for order, status in val.items():
            cur_point = point[int(order)]
            if status:
                score += int(cur_point.get('point'))
    old_statistics.update(score=score)
    train_rank.statistics = old_statistics
    train_rank.save()
    return old_statistics
