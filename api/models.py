from django.db import models
from django.utils import timezone


class OperationRecord(models.Model):
    """操作记录表 - 用于保存从小程序端传输过来的操作痕迹"""
    
    remark = models.CharField(
        max_length=200,
        default='新生报到操作',
        verbose_name='备注信息'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = '操作记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.remark} - {self.created_at}"
