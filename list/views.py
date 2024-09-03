from django.shortcuts                   import render, redirect
from .forms                             import RowForm
from .models                            import Row
from django.contrib.auth.decorators     import login_required
from django.contrib.auth.views          import LoginView, LogoutView
from django.urls                        import reverse_lazy
from datetime                           import datetime, timedelta
from django.http                        import HttpResponse
from django.contrib.auth.models         import User, Group
from collections                        import defaultdict
from django.db.models                   import Max

# Create your views here.


def indexv(request):
    if request.user.is_authenticated:
        return redirect('form')
    else:
        return redirect('login')


@login_required
def formv(request):
    
    is_admin = request.user.groups.filter(name="admin").exists()
    
    if request.method == 'POST':
        if 'update' in request.POST:
            date_str = request.POST.get('date')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')

            # Konwersja daty do formatu YYYY-MM-DD
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return HttpResponse('Nieprawidłowy format daty', status=400)

            # Usunięcie nakładających się wpisów
            Row.objects.filter(
                user=request.user,
                date=date,
                start_time__lt=end_time_str,
                end_time__gt=start_time_str
            ).delete()

            # Dodanie nowego wpisu
            form = RowForm(request.POST, user=request.user)
            if form.is_valid():
                row = form.save(commit=False)
                row.user = request.user
                row.save()
                return redirect('success')

        else:
            form = RowForm(request.POST, user=request.user)
            if form.is_valid():
                overlapping_rows = Row.objects.filter(
                    user=request.user,
                    date=form.cleaned_data['date'],
                    start_time__lt=form.cleaned_data['end_time'],
                    end_time__gt=form.cleaned_data['start_time']
                ).exclude(id=form.instance.id)  # Upewnij się, że nie porównujesz z samym sobą

                if overlapping_rows.exists():
                    return render(request, 'form/errors/form_with_confirm.html', {
                        'form': form,
                        'overlapping_rows': overlapping_rows,
                        'new_entry': form.cleaned_data,
                    })

                row = form.save(commit=False)
                row.user = request.user
                row.save()
                return redirect('success')
    else:
        form = RowForm(user=request.user)

    context = {
        'form': form,
        'is_admin': is_admin,
    }

    return render(request, 'form/form.html', context)


@login_required
def confirm_update(request):
    if request.method == 'POST':
        new_entry_data = request.session.get('new_entry')
        
        if not new_entry_data:
            return redirect('form')  # Jeśli brak danych, wracamy do formularza

        new_entry_data['date'] = datetime.strptime(new_entry_data['date'], '%Y-%m-%d').date()
        new_entry_data['start_time'] = datetime.strptime(new_entry_data['start_time'], '%H:%M:%S').time()
        new_entry_data['end_time'] = datetime.strptime(new_entry_data['end_time'], '%H:%M:%S').time()

        form = RowForm(new_entry_data, user=request.user)
        
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            overlapping_rows = Row.objects.filter(
                user=request.user,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=form.instance.id)

            if 'update' in request.POST:
                overlapping_rows.delete()
                row = form.save(commit=False)
                row.user = request.user
                row.save()
                del request.session['new_entry']
                return redirect('success')

            elif 'cancel' in request.POST:
                del request.session['new_entry']
                return redirect('form')

    return redirect('form')

       
def successv(request):
    return render(request, 'form/errors/success.html', {})


@login_required
def reportv(request):
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Lista miesięcy po polsku
    months_polish = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]

    # Lista miesięcy od 1 do 12
    months = list(range(1, 13))

    # Zakładamy, że chcesz pokazać ostatnie 10 lat
    years = range(current_year - 10, current_year + 1)

    # Pobranie użytkowników
    users = User.objects.all()

    # Pobranie wybranego użytkownika z zapytania GET, domyślnie ustaw na zalogowanego użytkownika
    selected_user_id = int(request.GET.get('user', request.user.id))
    selected_user = User.objects.get(id=selected_user_id)

    # Sprawdzanie, czy zalogowany użytkownik należy do grupy "kierownik"
    is_manager = request.user.groups.filter(name="kierownik").exists()

    # Jeżeli użytkownik nie jest kierownikiem, może zobaczyć tylko swoje własne dane
    if not is_manager and selected_user != request.user:
        return redirect('reportv')  # przekieruj na stronę z danymi tylko dla zalogowanego użytkownika

    # Pobranie wybranego miesiąca i roku z zapytania GET
    selected_month = int(request.GET.get('month', current_month))
    selected_year = int(request.GET.get('year', current_year))

    # Filtrowanie danych
    rows = Row.objects.filter(
        user=selected_user,
        date__month=selected_month,
        date__year=selected_year
    ).order_by('date', 'start_time')

    # Grupowanie danych po dacie i wybieranie największych wartości
    grouped_rows = defaultdict(lambda: {"total_hours": timedelta(), "overtime_hours": timedelta(), "last_row": None})
    for row in rows:
        grouped_data = grouped_rows[row.date]
        
        # Użyj total_seconds() do porównania czasu pracy
        grouped_data["total_hours"] = max(grouped_data["total_hours"], row.total_hours, key=lambda x: x.total_seconds())
        grouped_data["overtime_hours"] = max(grouped_data["overtime_hours"], row.overtime_hours, key=lambda x: x.total_seconds())
        grouped_data["last_row"] = row  # Zachowaj ostatni wpis dla tej daty

    # Przygotowanie listy ostatecznych wierszy do wyświetlenia
    final_rows = []
    for date, data in grouped_rows.items():
        row = data["last_row"]
        row.total_hours = data["total_hours"]
        row.overtime_hours = data["overtime_hours"]
        final_rows.append(row)

    # Przypisanie polskiej nazwy miesiąca
    selected_month_name = months_polish[selected_month - 1]

    context = {
        'rows': rows,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
        'selected_year': selected_year,
        'months': months,
        'years': years,
        'users': users,
        'selected_user': selected_user,
        'is_manager': is_manager,
    }

    return render(request, 'main/report.html', context)


class loginv(LoginView):
    template_name = 'login/login.html'

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'form': form,
        })

    
class logoutv(LogoutView):
    next_page = reverse_lazy('login')