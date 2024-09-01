from django.shortcuts                   import render, redirect
from .forms                             import RowForm
from .models                            import Row
from django.contrib.auth.decorators     import login_required
from django.contrib.auth.views          import LoginView, LogoutView
from django.urls                        import reverse_lazy
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
        form = RowForm(request.POST, user=request.user)
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

            if overlapping_rows.exists():
                # Renderujemy stronę potwierdzenia wyboru
                return render(request, 'form/confirm_update.html', {
                    'form': form,
                    'overlapping_rows': overlapping_rows
                })

            # Jeśli nie ma nakładających się wierszy, zapisujemy nowy wpis
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
        form = RowForm(request.POST, user=request.user)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            overlapping_rows = Row.objects.filter(
                user=request.user,
                date=date,
                start_time__lt=end_time,
                end_time__g=start_time
            ).exclude(id=form.instance.id)

            if 'update' in request.POST:
                overlapping_rows.delete()  # Usunięcie nakładających się wpisów
                row = form.save(commit=False)
                row.user = request.user
                row.save()
                return redirect('success')

            elif 'cancel' in request.POST:
                return redirect('form')  # Przekierowanie na stronę główną

    return redirect('form')  # Powrót do formularza w przypadku niepowodzenia


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