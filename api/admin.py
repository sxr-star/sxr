from django.contrib import admin
from .models import OperationRecord


@admin.register(OperationRecord)
class OperationRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'remark', 'created_at']
    search_fields = ['remark']
    list_filter = ['created_at']
    ordering = ['-created_at']
