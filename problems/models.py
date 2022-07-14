from django.db import models
from django.utils.translation import gettext_lazy as _
from organization.models import User
from utils.models import RichTextField


class ProblemTag(models.Model):
    tag_name = models.CharField("标签名称", max_length=6)

    class Meta:
        db_table = "problem_tag"


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EAZY = 'Easy', _('简单')
        MEDIUM = 'Medium', _('中等')
        HARD = 'HARD', _('困难')

    is_public = models.BooleanField("是否公开", default=False)
    title = models.CharField("题目名称", max_length=10)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    last_update_time = models.DateTimeField("最后更新时间", null=True)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(ProblemTag)
    source = models.CharField("题源", null=True)

    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    hint = RichTextField(null=True)
    languages = models.JSONField()
    template = models.JSONField()

    # ms
    time_limit = models.IntegerField("时间限制")
    # MB
    memory_limit = models.IntegerField("内存限制")

    commit_num = models.BigIntegerField("提交次数", default=0)
    accept_num = models.BigIntegerField("通过数", default=0)
    info = models.JSONField(default=dict)
    difficulty = models.CharField("难度", choices=Difficulty.choices)

    class Meta:
        db_table = "problem"
        ordering = "create_time"
