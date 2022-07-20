from django.db import models
from django.utils.translation import gettext_lazy as _

from contest.models import Contest
from organization.models import User


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
    source = models.CharField("题源", null=True, max_length=12)
    contest = models.ManyToManyField("被引用到比赛", to=Contest)
    visible = models.BooleanField("是否可见", default=True)

    description = models.TextField("问题描述")
    input_description = models.TextField("输入描述")
    output_description = models.TextField("输出描述")
    samples = models.JSONField("输入输出样例")
    hint = models.TextField("提示", null=True)
    languages = models.JSONField("问题支持语言")
    template = models.JSONField("代码模板")

    # ms
    time_limit = models.IntegerField("时间限制")
    # MB
    memory_limit = models.IntegerField("内存限制")

    commit_num = models.BigIntegerField("提交次数", default=0)
    accept_num = models.BigIntegerField("通过数", default=0)
    statistics_info = models.JSONField("问题数据", default=dict)
    difficulty = models.CharField("难度", choices=Difficulty.choices, max_length=6)

    class Meta:
        db_table = "problem"
        ordering = ['-create_time']
