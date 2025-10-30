from django.contrib import admin
from .models import CSVProcessingRecord, EmailRecord


@admin.register(CSVProcessingRecord)
class CSVProcessingRecordAdmin(admin.ModelAdmin):
    list_display = ['filename', 'processed_at', 'total_rows', 'successful_rows', 'failed_rows', 'status']
    list_filter = ['status', 'processed_at']
    search_fields = ['filename']
    readonly_fields = ['processed_at']


@admin.register(EmailRecord)
class EmailRecordAdmin(admin.ModelAdmin):
    list_display = ['email_address', 'zip_code', 'state', 'city', 'success', 'processed_at']
    list_filter = ['success', 'processed_at', 'state']
    search_fields = ['email_address', 'zip_code', 'state', 'city']
    readonly_fields = ['processed_at']

