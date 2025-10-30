from django.db import models


class CSVProcessingRecord(models.Model):
    """Record of CSV file processing"""
    filename = models.CharField(max_length=255)
    processed_at = models.DateTimeField(auto_now_add=True)
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='pending')
    
    class Meta:
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.filename} - {self.processed_at}"


class EmailRecord(models.Model):
    """Record of individual email processing"""
    processing_record = models.ForeignKey(CSVProcessingRecord, on_delete=models.CASCADE, related_name='emails')
    email_address = models.EmailField()
    zip_code = models.CharField(max_length=10)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.email_address} - {self.zip_code}"

