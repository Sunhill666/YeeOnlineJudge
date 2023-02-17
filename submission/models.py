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

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    """
    token = [token_1, token_2, ...]
    """
    token = models.JSONField(_("submission token"), default=list)
    code = models.TextField(_("submitted code"))
    language_id = models.IntegerField(_("submitted language"))
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)
    status = models.CharField(_("submitted status"), max_length=20, choices=Status.choices)
    created_time = models.DateTimeField(_("submitted time"), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def translate_status(status_dict):
        if 6 < status_dict.get('id') < 13:
            return Submission.Status.RE
        return Submission.Status(status_dict.get('description'))

    class Meta:
        db_table = 'submission'


prob_status = {
    "In Queue": 1,
    "Processing": 2,
    "Accepted": 3,
    "Wrong Answer": 4,
    "Time Limit Exceeded": 5,
    "Compilation Error": 6,
    "Runtime Error": 7,
    "Internal Error": 13,
    "Exec Format Error": 14
}
