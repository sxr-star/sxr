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
    list_display = ['id', 'name', 'student_id', 'phone', 'review_status_display', 'dormitory_number_display', 'has_id_card_photo_front', 'has_id_card_photo_back', 'created_at']
    search_fields = ['student_id', 'name', 'phone']
    list_filter = ['review_status', 'created_at']
    ordering = ['-created_at']
    actions = ['approve_selected', 'reject_selected']

    def review_status_display(self, obj):
        status_map = {'pending': '待审核', 'approved': '审核通过', 'rejected': '审核驳回'}
        return status_map.get(obj.review_status, obj.review_status)
    review_status_display.short_description = '审核状态'

    def dormitory_number_display(self, obj):
        return obj.dormitory_number or '-'
    dormitory_number_display.short_description = '宿舍号'

    def has_id_card_photo_front(self, obj):
        return bool(obj.id_card_photo_front)
    has_id_card_photo_front.boolean = True
    has_id_card_photo_front.short_description = '已上传正面照片'

    def has_id_card_photo_back(self, obj):
        return bool(obj.id_card_photo_back)
    has_id_card_photo_back.boolean = True
    has_id_card_photo_back.short_description = '已上传反面照片'

    @admin.action(description='审核通过选中记录')
    def approve_selected(self, request, queryset):
        queryset.update(review_status='approved', reject_reason=None)
        self.message_user(request, f'已审核通过 {queryset.count()} 条记录')

    @admin.action(description='审核驳回选中记录')
    def reject_selected(self, request, queryset):
        queryset.update(review_status='rejected', dormitory_number=None)
        self.message_user(request, f'已驳回 {queryset.count()} 条记录')


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
