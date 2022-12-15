from time import sleep

from celery import shared_task
from django.core.cache import cache
from django.db.models import Q

from contest.models import ContestRank, Contest
from organization.models import UserProfile
from submission.models import Submission
from utils.judger import submission
from utils.tools import get_judge_client


def judge_status(token):
    judge_client = get_judge_client()
    sub = submission.get(judge_client, token)
    while sub.status.get("id") < 3:
        sleep(0.5)
        sub.load(judge_client)
    return sub


@shared_task
def process_status(token):
    submit = Submission.objects.get(pk=token)
    sub = judge_status(token)
    submit.status = Submission.translate_status(sub.status)
    submit.save()


@shared_task
def process_statistics(token):
    submit = Submission.objects.get(pk=token)
    problem = submit.problem
    user_profile = UserProfile.objects.get(user=submit.commit_by)

    while submit.status == Submission.Status.IQ or submit.status == Submission.Status.PROCESSING:
        submit = Submission.objects.get(pk=token)

    # 更新Problem数据
    status_len = len(
        Submission.objects.filter(Q(problem=problem) & Q(status=submit.status) & Q(contest_id__isnull=True))
        .values('commit_by_id').distinct())
    accept_len = len(Submission.objects.filter(
        Q(problem=problem) & Q(status=Submission.Status.ACCEPTED) & Q(contest_id__isnull=True))
                     .values('commit_by_id').distinct())
    problem.statistics.update({submit.status: status_len})
    problem.accepted_num = accept_len

    # 更新UserProfile数据
    user_problem = cache.get(submit.commit_by.username, dict())
    prev_status = user_problem.get(submit.problem.id, None)

    # 前一状态为通过不更新
    if prev_status == Submission.Status.ACCEPTED:
        return

    # 前一状态为空则查询并更新前一状态
    if not prev_status:
        flag = True
        for i in user_profile.statistics.keys():
            tmp = user_profile.statistics.get(submit.status, list())
            if submit.problem.id in tmp:
                if tmp == Submission.Status.ACCEPTED:
                    return
                prev_status = i
                flag = False
                break
        if flag:
            prev_status = submit.status

    prev_list = user_profile.statistics.get(prev_status, list())

    # 更新数据中各项状态的题目列表并缓存
    if submit.problem.id in prev_list:
        prev_list.remove(submit.problem.id)
    cur_list = prev_list.copy()
    cur_list.append(submit.problem.id)
    user_profile.statistics.update({prev_status: list(set(prev_list))})
    user_profile.statistics.update({submit.status: list(set(cur_list))})
    user_problem.update({submit.problem.id: submit.status})
    cache.set(submit.commit_by.username, user_problem, None)

    user_accept_len = len(
        Submission.objects.filter(
            Q(commit_by=submit.commit_by) & Q(status=Submission.Status.ACCEPTED) & Q(contest_id__isnull=True))
        .values('problem_id').distinct())
    user_profile.accepted_num = user_accept_len

    user_profile.save()
    problem.save()


@shared_task
def contest_rank(token, contest_id):
    submit = Submission.objects.get(pk=token)
    user = submit.commit_by
    user_rank = ContestRank.objects.get(Q(contest_id=contest_id) & Q(user=user))
    contest = Contest.objects.get(pk=contest_id)
    score = contest.score

    while submit.status == Submission.Status.IQ or submit.status == Submission.Status.PROCESSING:
        submit = Submission.objects.get(pk=token)

    user_rank.accepted_num = len(Submission.objects.filter(
        Q(commit_by=user) & Q(contest=contest_id) & Q(status=Submission.Status.ACCEPTED))
                                 .values('problem_id').distinct())
    if not user_rank.problem.get(str(submit.problem.id), False):
        if submit.status == Submission.Status.ACCEPTED:
            user_rank.score += score.get(str(submit.problem.id))
            user_rank.problem.update({str(submit.problem.id): True})
        else:
            user_rank.problem.update({str(submit.problem.id): False})

    user_rank.save()
