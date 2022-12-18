from django.db import models

from organization.models import User
from training.models import Training


class Announcement(models.Model):
    title = models.CharField("文章题目", max_length=30)
    content = models.TextField("文章内容")
    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    last_update_time = models.DateTimeField("最后更新时间", null=True, auto_now=True)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='training', null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    visible = models.BooleanField("是否可见", default=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "announcement"
        ordering = ['id']
