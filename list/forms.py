from django                 import forms
from .models                import Row
from django.core.exceptions import ValidationError


class RowForm(forms.ModelForm):
    class Meta:
        model = Row
        fields = ['date', 'start_time', 'end_time', 'desc', 'type']
        widgets = {
            'date': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Przypisanie użytkownika do atrybutu obiektu
        super().__init__(*args, **kwargs)

        if self.user:
            last_row = Row.objects.filter(user=self.user).order_by('-date').first()
            cleanDesc = ''
            cleanType = 1
            if last_row:
                self.fields['start_time'].initial = last_row.start_time
                self.fields['end_time'].initial = last_row.end_time
            self.fields['desc'].initial = cleanDesc
            self.fields['type'].initial = cleanType

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')

        if not (start_time and end_time and date):
            return cleaned_data

        overlapping_rows = Row.objects.filter(
            user=self.user,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if overlapping_rows.exists():
            raise ValidationError('Podane godziny pokrywają się z innymi wierszami.')

        return cleaned_data

    

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
