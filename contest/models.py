from django.db import models


class Contest(models.Model):
    title = models.CharField("比赛标题", max_length=25)
