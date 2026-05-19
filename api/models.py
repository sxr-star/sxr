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


class VerificationCode(models.Model):
    """验证码记录表 - 存储手机号验证码发送记录"""
    
    phone = models.CharField(
        max_length=11,
        verbose_name='手机号'
    )
    code = models.CharField(
        max_length=4,
        verbose_name='验证码'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='发送时间'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='是否已使用'
    )
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )

    class Meta:
        verbose_name = '验证码记录'
        verbose_name_plural = '验证码记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone} - {self.code}"


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
    id_card_photo_front = models.ImageField(
        upload_to='id_cards/%Y/%m/%d/',
        verbose_name='身份证正面照片',
        blank=True,
        null=True
    )
    id_card_photo_back = models.ImageField(
        upload_to='id_cards/%Y/%m/%d/',
        verbose_name='身份证反面照片',
        blank=True,
        null=True
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
