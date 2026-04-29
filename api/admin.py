from django.contrib import admin
from .models import OperationRecord, StudentInfo, RegistrationRecord


@admin.register(OperationRecord)
class OperationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'remark', 'created_at']
    search_fields = ['remark']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'student_id', 'phone', 'created_at']
    search_fields = ['student_id', 'name']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(RegistrationRecord)
class RegistrationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_name', 'student_id', 'register_time']
    list_filter = ['register_time']
    search_fields = ['student__student_id', 'student__name']
    ordering = ['-register_time']

    def student_name(self, obj):
        return obj.student.name
    student_name.short_description = '姓名'

    def student_id(self, obj):
        return obj.student.student_id
    student_id.short_description = '学号'
