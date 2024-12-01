import os
from PyPDF2 import PdfReader
from docx import Document
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import DocumentUploadForm, SummaryRequestForm
from .models import UploadedDocument, SummarizationHistory
from .nlp import summarize_text
from django.shortcuts import get_object_or_404, redirect

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        return " ".join([page.extract_text() for page in reader.pages])
    elif ext in [".doc", ".docx"]:
        doc = Document(file_path)
        return " ".join([p.text for p in doc.paragraphs])
    return ""

def upload_documents(request):
    summary = None  # Variable to store the summary
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        num_sentences_form = SummaryRequestForm(request.POST)
        if form.is_valid() and num_sentences_form.is_valid():
            document = form.save()
            num_sentences = num_sentences_form.cleaned_data['num_sentences']
            file_path = document.file.path
            text = extract_text_from_file(file_path)
            summary = summarize_text(text, num_sentences)

            history = SummarizationHistory.objects.create(
                title=os.path.basename(file_path),
                summary=summary,
                num_sentences=num_sentences,
            )
            return render(request, "upload.html", {
                "form": form,
                "num_sentences_form": num_sentences_form,
                "summary": summary  # Pass the summary to the template
            })
    else:
        form = DocumentUploadForm()
        num_sentences_form = SummaryRequestForm()

    return render(request, "upload.html", {"form": form, "num_sentences_form": num_sentences_form, "summary": summary})


def view_history(request):
    history = SummarizationHistory.objects.all()
    return render(request, "history.html", {"history": history})

def delete_history(request, history_id):
    history_entry = get_object_or_404(SummarizationHistory, id=history_id)
    history_entry.delete()
    return redirect('view_history')


def summarize_checked_history(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist('selected_entries')
        print(f"Selected IDs: {selected_ids}")  # Debugging

        if not selected_ids:
            print("No IDs selected.")  # Debugging
            return redirect('view_history')

        selected_entries = SummarizationHistory.objects.filter(id__in=selected_ids)
        combined_text = " ".join(entry.summary for entry in selected_entries)
        combined_summary = summarize_text(combined_text, num_sentences=10)

        return render(request, 'combined_summary.html', {
            'combined_summary': combined_summary,
            'selected_entries': selected_entries,
        })

    print("GET request received.")  # Debugging
    return redirect('view_history')