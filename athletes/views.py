from pathlib import Path

from django.contrib import messages
from django.shortcuts import redirect, render

from . import utils
from .forms import AthleteForm, UploadFileForm


def index(request):
    return render(request, 'athletes/index.html')


def add_athlete(request):
    if request.method == 'POST':
        form = AthleteForm(request.POST)
        if form.is_valid():
            athlete = {
                'name': form.cleaned_data['name'],
                'age': form.cleaned_data['age'],
                'sport': form.cleaned_data['sport'],
                'country': form.cleaned_data['country'],
                'achievements': form.cleaned_data['achievements'] or '',
            }
            filename = utils.save_athlete_to_file(athlete, form.cleaned_data['file_format'])
            messages.success(request, f'Данные сохранены в файл {filename}')
            return redirect('athletes:list_files')
    else:
        form = AthleteForm()
    return render(request, 'athletes/add_athlete.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES['file']
            ext = Path(uploaded.name).suffix.lower().lstrip('.')

            new_name = utils.generate_filename(ext)
            path = utils.DATA_DIR / new_name

            with open(path, 'wb+') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            try:
                utils.parse_data_file(path)
            except Exception as exc:
                path.unlink(missing_ok=True)
                messages.error(request, f'Файл невалиден и был удалён: {exc}')
                return render(request, 'athletes/upload_file.html', {'form': form})

            messages.success(request, f'Файл {new_name} успешно загружен и проверен')
            return redirect('athletes:list_files')
    else:
        form = UploadFileForm()

    return render(request, 'athletes/upload_file.html', {'form': form})


def list_files(request):
    files = utils.list_data_files()
    file_infos = []

    for p in files:
        info = {'name': p.name, 'format': p.suffix.lstrip('.').upper(),
                'records': [], 'error': None}
        try:
            info['records'] = utils.parse_data_file(p)
        except Exception as exc:
            info['error'] = str(exc)
        file_infos.append(info)

    return render(request, 'athletes/list_files.html', {'files': file_infos})