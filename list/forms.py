from django     import forms
from .models    import Row


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
        user = kwargs.pop('user', None)  # Odbierz zalogowanego użytkownika
        super().__init__(*args, **kwargs)

        if user:
            last_row = Row.objects.filter(user=user).order_by('-date').first()
            
            if last_row:
                self.fields['start_time'].initial = last_row.start_time
                self.fields['end_time'].initial = last_row.end_time

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
