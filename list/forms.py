from django     import forms
from .models    import Row
import re
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


class RowForm(forms.ModelForm):
    class Meta:
        model = Row
        fields = ['date', 'start_time', 'end_time', 'desc', 'type']
        widgets = {
            'date': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date'}),
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }