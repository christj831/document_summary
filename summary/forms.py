from django import forms
from .models import UploadedDocument

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ['file']

class SummaryRequestForm(forms.Form):
    num_sentences = forms.IntegerField(label="Number of sentences", min_value=1, max_value=10)
