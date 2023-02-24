from django.db.models.signals import pre_delete
from django.dispatch import receiver

from training.models import ProblemSet


# 接收 post_delete 信号无法查询关联
@receiver(pre_delete, sender=ProblemSet)
def ordering_sync_stage(sender, instance, **kwargs):
    for plan in instance.stages.all():
        plan.ordering.remove(instance.id)
        plan.save()
