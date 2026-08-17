from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .decorators import rol_requerido
from .models import CustomUser


def _error_para_mensaje(exc):
    """Convierte un ValidationError en un mensaje legible."""
    if hasattr(exc, 'message_dict'):
        return '; '.join(
            f'{campo}: {" ".join(errs)}' for campo, errs in exc.message_dict.items()
        )
    return '; '.join(str(e) for e in exc.messages)


def login_usuario(request):
    """Inicio de sesión (FBV): autentica y redirige según el rol."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        error = 'Usuario o contraseña incorrectos. Verifique sus credenciales.'
    return render(request, 'registration/login.html', {'error': error})


@require_http_methods(['POST'])
def logout_usuario(request):
    """Cierre de sesión (FBV)."""
    logout(request)
    return redirect('accounts:login')


def registro(request):
    """Registro de una nueva cuenta de usuario del sistema."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    errores = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if CustomUser.objects.filter(username=username).exists():
            errores = 'Ya existe un usuario con ese nombre de usuario.'
        elif not password1 or not password2:
            errores = 'Debe definir una contraseña y confirmarla.'
        elif password1 != password2:
            errores = 'Las contraseñas no coinciden.'
        else:
            try:
                validate_password(password1, user=None)
                usuario = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                )
                messages.success(
                    request,
                    f'Cuenta creada para {usuario.username}. Ya puedes iniciar sesión.',
                )
                return redirect('accounts:login')
            except ValidationError as exc:
                errores = _error_para_mensaje(exc)
    return render(request, 'accounts/registro.html', {
        'errores': errores,
        'datos': request.POST if request.method == 'POST' else None,
    })


@login_required
def perfil(request):
    """Muestra el perfil del usuario autenticado."""
    return render(request, 'accounts/perfil.html')


@login_required
@rol_requerido('ADMIN')
def lista_usuarios(request):
    """Listado de usuarios del sistema con búsqueda (solo administradores)."""
    q = request.GET.get('q', '').strip()
    usuarios = CustomUser.objects.all().order_by('username')
    if q:
        usuarios = usuarios.filter(
            username__icontains=q,
        ) | usuarios.filter(
            first_name__icontains=q,
        ) | usuarios.filter(
            last_name__icontains=q,
        ) | usuarios.filter(
            email__icontains=q,
        )
    return render(
        request,
        'accounts/usuario_list.html',
        {'usuarios': usuarios.distinct(), 'q': q},
    )


def _datos_usuario_desde_post(request):
    """Convierte el POST de gestión de usuarios en datos del CustomUser."""
    return {
        'username': request.POST.get('username', '').strip(),
        'first_name': request.POST.get('first_name', '').strip(),
        'last_name': request.POST.get('last_name', '').strip(),
        'email': request.POST.get('email', '').strip(),
        'role': request.POST.get('role', CustomUser.Role.ENFERMERO),
        'colegiatura': request.POST.get('colegiatura', '').strip(),
        'telefono': request.POST.get('telefono', '').strip(),
        'is_active': request.POST.get('is_active') == 'on',
    }


@login_required
@rol_requerido('ADMIN')
@require_http_methods(['GET', 'POST'])
def crear_usuario(request):
    """Creación de un usuario con rol desde la web (usa create_user)."""
    errores = None
    if request.method == 'POST':
        datos = _datos_usuario_desde_post(request)
        password = request.POST.get('password', '')
        if CustomUser.objects.filter(username=datos['username']).exists():
            errores = 'Ya existe un usuario con ese nombre de usuario.'
        elif not password:
            errores = 'La contraseña es obligatoria al crear un usuario.'
        else:
            try:
                validate_password(password, user=None)
                usuario = CustomUser.objects.create_user(
                    username=datos['username'],
                    email=datos['email'],
                    password=password,
                    first_name=datos['first_name'],
                    last_name=datos['last_name'],
                    is_active=datos['is_active'],
                )
                usuario.role = datos['role']
                usuario.colegiatura = datos['colegiatura']
                usuario.telefono = datos['telefono']
                usuario.save()
                messages.success(request, f'Usuario {usuario.username} creado correctamente.')
                return redirect('accounts:lista_usuarios')
            except ValidationError as exc:
                errores = _error_para_mensaje(exc)
    return render(request, 'accounts/usuario_form.html', {
        'titulo': 'Crear usuario',
        'roles': CustomUser.Role.choices,
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
    })


@login_required
@rol_requerido('ADMIN')
@require_http_methods(['GET', 'POST'])
def editar_usuario(request, pk):
    """Edición de un usuario: datos personales, rol y contraseña opcional."""
    usuario = get_object_or_404(CustomUser, pk=pk)
    errores = None
    if request.method == 'POST':
        datos = _datos_usuario_desde_post(request)
        if CustomUser.objects.exclude(pk=usuario.pk).filter(username=datos['username']).exists():
            errores = 'Ya existe un usuario con ese nombre de usuario.'
        else:
            for campo, valor in datos.items():
                setattr(usuario, campo, valor)
            password = request.POST.get('password', '')
            try:
                if password:
                    validate_password(password, user=usuario)
                    usuario.set_password(password)
                usuario.save()
                messages.success(request, f'Usuario {usuario.username} actualizado.')
                return redirect('accounts:lista_usuarios')
            except ValidationError as exc:
                errores = _error_para_mensaje(exc)
    return render(request, 'accounts/usuario_form.html', {
        'titulo': f'Editar usuario: {usuario.username}',
        'usuario': usuario,
        'roles': CustomUser.Role.choices,
        'datos': request.POST if request.method == 'POST' else None,
        'errores': errores,
    })


@login_required
@rol_requerido('ADMIN')
@require_http_methods(['POST'])
def retirar_usuario(request, pk):
    """Retiro lógico de un usuario: cambia su estado, nunca lo elimina."""
    usuario = get_object_or_404(CustomUser, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puede desactivar su propia cuenta.')
    else:
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        if usuario.is_active:
            messages.success(request, f'Usuario {usuario.username} reactivado.')
        else:
            messages.success(request, f'Usuario {usuario.username} desactivado.')
    return redirect('accounts:lista_usuarios')