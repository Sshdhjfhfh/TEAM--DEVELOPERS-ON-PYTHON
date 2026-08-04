from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):
    """Registro de una nueva cuenta de usuario del sistema."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(
            request,
            f'Cuenta creada para {user.username}. Ya puedes iniciar sesión.',
        )
        return redirect('accounts:login')
    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def perfil(request):
    """Muestra el perfil del usuario autenticado."""
    return render(request, 'accounts/perfil.html')
