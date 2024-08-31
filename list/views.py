from django.shortcuts                   import render, redirect
from .forms                             import RowForm
from django.contrib.auth.decorators     import login_required
from django.contrib.auth.views          import LoginView, LogoutView
from django.urls                        import reverse_lazy

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
            row = form.save(commit=False)
            row.user = request.user
            row.save()
    else:
        form = RowForm()
    return render(request, 'form/form.html', {'form': form})

class loginv(LoginView):
    template_name = 'login/login.html'

    def form_invalid(self, form):
        # Renderowanie szablonu logowania z komunikatem o błędzie
        return render(self.request, self.template_name, {
            'form': form,
        })
    
class logoutv(LogoutView):
    next_page = reverse_lazy('login')