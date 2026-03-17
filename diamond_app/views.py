import os
import uuid
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .transform import process_csv

def dashboard(request):
    context = {}

    if request.method == 'POST':
        uploaded_file = request.FILES.get('csv_file')

        if not uploaded_file:
            context['error'] = 'select a CSV file to upload.'
            return render(request, 'diamond_app/dashboard.html', context)

        if not uploaded_file.name.endswith('.csv'):
            context['error'] = 'Only CSV files allow.'
            return render(request, 'diamond_app/dashboard.html', context)

        try:
            csv_content, input_count, output_count = process_csv(uploaded_file)

            output_filename = f"output_{uuid.uuid4().hex[:8]}.csv"
            output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
            os.makedirs(output_dir, exist_ok=True)

            with open(os.path.join(output_dir, output_filename), 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)

            context['success'] = True
            context['output_filename'] = output_filename

        except Exception as e:
            context['error'] = f'Error processing file: {str(e)}'

    return render(request, 'diamond_app/dashboard.html', context)


def download_output(request, filename):
    output_path = os.path.join(settings.MEDIA_ROOT, 'outputs', filename)

    if not os.path.exists(output_path):
        return HttpResponse('File not found.', status=404)

    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="output_data.csv"'
    return response