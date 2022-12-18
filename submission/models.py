from django.db import models
from django.utils.translation import gettext_lazy as _

from organization.models import User
from problem.models import Problem
from training.models import Training


class Submission(models.Model):
    class Status(models.TextChoices):
        IQ = 'In Queue', _('队列中')
        PROCESSING = 'Processing', _('运行中')
        ACCEPTED = 'Accepted', _('正确')
        WA = 'Wrong Answer', _('答案错误')
        TLE = 'Time Limit Exceeded', _('超时')
        CE = 'Compilation Error', _('编译错误')
        RE = 'Runtime Error', _('运行错误')
        IE = 'Internal Error', _('内部错误')
        EFE = 'Exec Format Error', _('运行格式错误')

    commit_by = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    token = models.CharField("提交token", max_length=36, primary_key=True)
    code = models.TextField("提交的代码")
    language_id = models.IntegerField("提交语言ID")
    created_time = models.DateTimeField("提交时间", auto_now_add=True)
    status = models.CharField("状态", max_length=20, choices=Status.choices)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)

    @staticmethod
    def translate_status(status_dict):
        status_id = status_dict.get('id')
        if 6 < status_id < 13:
            return Submission.Status.RE
        return Submission.Status(status_dict.get('description'))

    class Meta:
        db_table = 'submission'
