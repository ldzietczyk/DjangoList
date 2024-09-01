from django.shortcuts                   import render, redirect
from .forms                             import RowForm
from .models                            import Row
from django.contrib.auth.decorators     import login_required
from django.contrib.auth.views          import LoginView, LogoutView
from django.urls                        import reverse_lazy
from datetime                           import datetime
from django.http                        import HttpResponse

# Create your views here.


def indexv(request):
    if request.user.is_authenticated:
        return redirect('form')
    else:
        return redirect('login')


@login_required
def formv(request):
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

    return render(request, 'form/form.html', {'form': form})


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


class loginv(LoginView):
    template_name = 'login/login.html'

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'form': form,
        })

    
class logoutv(LogoutView):
    next_page = reverse_lazy('login')