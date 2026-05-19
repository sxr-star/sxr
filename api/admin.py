from django.contrib import admin
from .models import OperationRecord, StudentInfo, RegistrationRecord, VerificationCode


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'code', 'is_used', 'created_at', 'expires_at']
    search_fields = ['phone', 'code']
    list_filter = ['is_used', 'created_at']
    ordering = ['-created_at']


@admin.register(OperationRecord)
class OperationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'remark', 'created_at']
    search_fields = ['remark']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(StudentInfo)
class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'student_id', 'phone', 'has_id_card_photo_front', 'has_id_card_photo_back', 'is_name_verified', 'created_at']
    search_fields = ['student_id', 'name', 'phone']
    list_filter = ['created_at', 'is_name_verified']
    ordering = ['-created_at']
    actions = ['verify_name', 'reject_name']

    def has_id_card_photo_front(self, obj):
        return bool(obj.id_card_photo_front)
    has_id_card_photo_front.boolean = True
    has_id_card_photo_front.short_description = '已上传正面照片'

    def has_id_card_photo_back(self, obj):
        return bool(obj.id_card_photo_back)
    has_id_card_photo_back.boolean = True
    has_id_card_photo_back.short_description = '已上传反面照片'

    @admin.action(description='审核通过：姓名与身份证一致')
    def verify_name(self, request, queryset):
        queryset.update(is_name_verified=True)

    @admin.action(description='审核不通过：姓名与身份证不一致')
    def reject_name(self, request, queryset):
        queryset.update(is_name_verified=False)


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
