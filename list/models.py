from django.db              import models
from django.conf            import settings
import datetime            #import datetime
from django                 import forms
from django.conf            import settings
from django.forms.widgets   import Select


# Create your models here.

class Row(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    
    date = models.DateField(
        'Podaj datę: ',
        default=datetime.date.today,
    )
    
    start_time = models.TimeField(
        'Godzina rozpoczęcia: ',
    )
    
    end_time = models.TimeField(
        'Godzina zakoczenia: ',
    )
    
    desc = models.CharField(
        'Opis: ',
        max_length=150,
        blank=True,
    )
    work = [
        (1, 'Zwykły czas pracy'),
        (2, 'Nadgodziny'),
        (3, 'Urlop'),
        (4, 'Zwolnienie lekarskie'),
        (5, 'Opieka nad dzieckiem'),
    ]

    type = models.IntegerField(
        'Wybierz rodzaj pracy:',
        choices=work,
        default=1,
    )
