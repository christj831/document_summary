from django.db import models

class UploadedDocument(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class SummarizationHistory(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    num_sentences = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    