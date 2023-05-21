from django.db import models
from django.utils.translation import gettext_lazy as _

from organization.models import User
from utils.tools import default_statistics


class ProblemTag(models.Model):
    tag_name = models.CharField(_("tag name"), max_length=20, unique=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        db_table = "problem_tag"
        ordering = ['tag_name']


class TestCase(models.Model):
    file = models.FileField(upload_to='test_case')
    created_time = models.DateTimeField(_("upload date"), auto_now_add=True)
    struct = models.JSONField(_("struct of test case"))

    class Meta:
        db_table = "test_case"
        ordering = ['id']


class Picture(models.Model):
    pic = models.ImageField(upload_to='pics/')

    class Meta:
        db_table = "picture"
        ordering = ['id']


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EAZY = 'Easy', _('easy')
        MEDIUM = 'Medium', _('medium')
        HARD = 'Hard', _('hard')

    class Mode(models.TextChoices):
        OI = 'OI', _('OI')
        ACM = 'ACM', _('ACM')

    title = models.CharField(_("problem name"), max_length=30)
    desc = models.TextField(_("problem description"))
    input_desc = models.TextField(_("input description"))
    output_desc = models.TextField(_("output description"))
    '''
    {
        "samples": [
            {"input": "1 2\n3 4\n", "output": "3\n7\n"}, 
            {"input": "0 2\n-1 4\n", "output": "2\n3\n"},
            ...
        ]
    }
    '''
    sample = models.JSONField(_("input output sample"), null=True)
    '''
    {
        "50": "//PREPEND BEGIN\n#include <stdio.h>\n//PREPEND END\n\n//TEMPLATE BEGIN\nint add(int a, int b) {\n  // 
    Please fill this blank\n  return ___________;\n}\n//TEMPLATE END\n\n//APPEND BEGIN\nint main() {\n  printf(\"%d\", 
    add(1, 2));\n  return 0;\n}\n//APPEND END",
        "<language_id>": "…………"
    }
    '''
    template = models.JSONField(_("completion template"), null=True)
    hint = models.TextField(_("hint"), null=True, blank=True)
    '''
    {
        "languages": [<language_id>, ...]
    }
    '''
    languages = models.JSONField(_("problem support languages"))
    # MS
    time_limit = models.IntegerField(_("time limit"))
    # MB
    memory_limit = models.IntegerField(_("memory limit"))
    difficulty = models.CharField(_("difficulty"), choices=Difficulty.choices, max_length=6)
    mode = models.CharField(_("problem mode"), choices=Mode.choices, max_length=4, default=Mode.ACM)
    test_case = models.ForeignKey(TestCase, on_delete=models.PROTECT, related_name="cases")
    '''
    In ACM and OI mode:
    [
        // test_case #1
        {
            "input_name": "1.in",
            "output_name": "1.out",
            "point": 50 // ignore in ACM mode
        },

        // test_case #2
        {
            "input_name": "2.in",
            "output_name": "2.out",
            "point": 50 // ignore in ACM mode
        }
    ]
    '''
    point = models.JSONField(_("test case structure and each point"))

    # 面向前台显示
    is_public = models.BooleanField(_("public"), default=False)
    tags = models.ManyToManyField(ProblemTag, related_name='problems')
    source = models.CharField(_("problem source"), null=True, blank=True, max_length=30)
    # 面向工作人员显示
    visible = models.BooleanField(_("visible"), default=True)

    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    last_update_time = models.DateTimeField(_("last update time"), auto_now=True)
    '''
    {
        "commit": 20,
        "accepted": 17,
        ...
    }
    '''
    statistics = models.JSONField(_("problem statistics"), default=default_statistics)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='creator')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "problem"
        ordering = ['id']
