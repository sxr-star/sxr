from django.db import models
from django.utils import timezone


class OperationRecord(models.Model):
    """操作记录表 - 用于保存从小程序端传输过来的操作痕迹（1.0版本保留）"""
    
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


class StudentInfo(models.Model):
    """学生信息表 - 存储新生个人基本信息"""
    
    name = models.CharField(
        max_length=50,
        verbose_name='姓名'
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='学号'
    )
    phone = models.CharField(
        max_length=11,
        verbose_name='手机号'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '学生信息'
        verbose_name_plural = '学生信息'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.student_id}"


class RegistrationRecord(models.Model):
    """报到记录表 - 存储新生报到记录，与学生信息一对一关联"""
    
    student = models.OneToOneField(
        StudentInfo,
        on_delete=models.CASCADE,
        verbose_name='学生信息'
    )
    register_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='报到时间'
    )

    class Meta:
        verbose_name = '报到记录'
        verbose_name_plural = '报到记录'
        ordering = ['-register_time']

    def __str__(self):
        return f"{self.student.name} - {self.register_time}"
