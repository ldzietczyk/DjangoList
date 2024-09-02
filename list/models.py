from django.db              import models
from django.conf            import settings
import datetime            #import datetime
from django.conf            import settings
from django.db.models       import Sum, F, DurationField, ExpressionWrapper


# Create your models here.

class Row(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    
    date = models.DateField(
        'Podaj datę',
        default=datetime.date.today,
    )
    
    start_time = models.TimeField(
        'Godzina rozpoczęcia',
        default='00:00'
    )
    
    end_time = models.TimeField(
        'Godzina zakoczenia',
        default='01:00'
    )
    
    desc = models.CharField(
        'Opis',
        max_length=150,
        blank=True,
    )
    work = [
        (1, 'Zwykły czas pracy'),
        (2, 'Nadgodziny'),
        (3, 'Urlop'),
        (4, 'Zwolnienie lekarskie'),
        (5, 'Opieka nad dzieckiem'),
        (6, 'Praca zdalna'),
    ]

    type = models.IntegerField(
        'Wybierz rodzaj pracy',
        choices=work,
        default=1,
    )
    
    total_hours = models.DurationField(
        'Całkowity czas pracy', 
        default=datetime.timedelta,
    )
    overtime_hours = models.DurationField(
        'Całkowity czas nadgodzin', 
        default=datetime.timedelta,
    )

    def save(self, *args, **kwargs):
        # Oblicz różnicę czasu między start_time a end_time
        work_duration = datetime.datetime.combine(datetime.date.today(), self.end_time) - \
                        datetime.datetime.combine(datetime.date.today(), self.start_time)

        if self.type == 2:
            self.overtime_hours = work_duration
            self.total_hours = datetime.timedelta(0)  # Nadgodziny są liczone osobno
        else:
            self.total_hours = work_duration
            self.overtime_hours = datetime.timedelta(0)  # Zwykłe godziny pracy nie są nadgodzinami

        super(Row, self).save(*args, **kwargs)