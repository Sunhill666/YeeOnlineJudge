from django.db import models
from django.utils.translation import gettext_lazy as _

from organization.models import Group, User
from problem.models import Problem


class ProblemSet(models.Model):
    title = models.CharField(_("title"), max_length=25)
    problems = models.ManyToManyField(Problem, related_name='problem')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'problem_set'
        ordering = ['id']


class Contest(models.Model):
    title = models.CharField(_("title"), max_length=25)
    description = models.TextField(_("description"), max_length=100)
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    start_time = models.DateTimeField(_("start time"))
    end_time = models.DateTimeField(_("end time"))
    stage = models.ManyToManyField(ProblemSet, related_name='stages')
    '''
    [31, 29, 32] # Problem Set ID
    '''
    ordering = models.JSONField(_("ordering of stage"))
    mode = models.CharField(_("contest mode"), choices=Problem.Mode.choices, max_length=4)

    group = models.ManyToManyField(Group, related_name='con_group')
    user = models.ManyToManyField(User, related_name='con_user')
    password = models.CharField(_("password"), max_length=128, null=True)
    is_open = models.BooleanField(_("open whether or not"), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='con_creator')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'contest'
        ordering = ['id']


class ContestRank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    '''
    {
        # Problem Set ID: {
            Problem ID: True | False | None
        }
        
        1: {
            1: True,
            2: False,
            3: None,
        },
        2: {
            1: True,
            2: False,
            3: None,
        },
        "score": 10
    }
    '''
    statistics = models.JSONField(_("contest statistics"), default=dict)

    class Meta:
        db_table = 'contest_rank'
        ordering = ['id']
