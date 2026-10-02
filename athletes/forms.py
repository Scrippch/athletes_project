from django import forms


class AthleteForm(forms.Form):
    name = forms.CharField(
        max_length=100, label='ФИО',
        error_messages={'required': 'Укажите ФИО'}
    )
    age = forms.IntegerField(
        min_value=10, max_value=100, label='Возраст',
        error_messages={
            'required': 'Укажите возраст',
            'min_value': 'Возраст не может быть меньше 10',
            'max_value': 'Возраст не может быть больше 100',
            'invalid': 'Возраст должен быть целым числом',
        }
    )
    sport = forms.CharField(max_length=50, label='Вид спорта')
    country = forms.CharField(max_length=50, label='Страна')
    achievements = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 3}),
        label='Достижения'
    )
    file_format = forms.ChoiceField(
        choices=[('json', 'JSON'), ('xml', 'XML')],
        initial='json', label='Формат файла'
    )


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Файл (.json или .xml)')

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith(('.json', '.xml')):
            raise forms.ValidationError('Разрешены только файлы формата .json или .xml')
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Файл слишком большой (макс. 5 МБ)')
        return f