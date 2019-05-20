# -*- coding: utf-8 -*-
import re
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from .forms import DoctorForm, PacienteForm, DiagnosticoForm, RecipeForm
from .models import Doctor, Paciente, Diagnostico, FotoDiagnostico, Recipe
from django.http import JsonResponse
import requests, json

def inicio(request):
    """
    Si el usuario hace click en el botón Inicio de la barra superior,
    es redirigido si ha iniciado sesión en el sistema.
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    if not request.user.is_authenticated():
        return render(request, 'inicio.html')

    # Ir a la página principal del doctor
    doctor_id = get_object_or_404(Doctor, user_ptr_id=request.user.id)
    pacientes = Paciente.objects.filter(doctor=doctor_id)
    return render(request, "doctor_principal.html", {
        "doctor_id": doctor_id,
        'pacientes': pacientes,
    })


def doctor_principal(request, doctor_id):
    """
    Si el usuario hace click en el botón Doctor de la barra superior,
    es redirigido si ha iniciado sesión.
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    # Ir a la página principal del doctor
    doctor_id = get_object_or_404(Doctor, pk=doctor_id)
    pacientes = Paciente.objects.filter(doctor=doctor_id)
    return render(request, "doctor_principal.html", {
        'doctor_id': doctor_id,
        'pacientes': pacientes,
    })


def agregar_diagnostico(request, paciente_id):
    """
    Agrega un diagnóstico asociado al paciente que se recibe por parámetros.
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    form = DiagnosticoForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'paciente_id': paciente,
        'doctor_id': paciente.doctor,
    }

    # Si el usuario ha llenado los campos de manera exitosa, el diagnóstico es
    # guardado y sus fotos también
    if form.is_valid():
        diagnostico = form.save(commit=False)
        diagnostico.paciente = paciente
        diagnostico.doctor = paciente.doctor
        peso = form.cleaned_data.get('peso')
        estatura = form.cleaned_data.get('estatura')
        estatura /= 100
        diagnostico.imc = peso / (estatura*estatura)
        diagnostico.save()

        # Se guardan las fotos del diagnóstico en el diagnostico
        for foto in request.FILES.values():
            diagnostico.agregar_foto(foto)

        return HttpResponseRedirect("/paciente/%s" % str(paciente_id))
    return render(request, "registrar_diagnostico.html", context)


def paciente_principal(request, paciente_id):
    """
    Muestra la página principal de un paciente en donde se muestran sus
    diagnósticos en una lista desplegable
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    diagnosticos = paciente.get_diagnosticos()
    context = {
        'paciente_id': paciente,
        "doctor_id": paciente.doctor,
        'diagnosticos': diagnosticos,
    }
    return render(request, "paciente_principal.html", context)


def editar_doctor(request, doctor_id):
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/doctor/%s" % str(doctor_id))

    return render(request, "editar_doctor.html", {
        "doctor_id": doctor,
        "form": form,
    })



def ver_diagnostico(request, doctor_id):
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    form = DoctorForm(request.POST or None, instance=doctor)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/doctor/%s" % str(doctor_id))

    return render(request, "diagnostico.html", {
        "doctor_id": doctor,
        "form": form,
    })


def editar_paciente(request, paciente_id):
    """
    Permite actualizar los datos de un paciente registrado en el sistema
    por un doctor
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    # Si los datos ingresados al momento de actualizar el paciente son validos,
    # todos sus datos son guardados.
    paciente_id = get_object_or_404(Paciente, pk=paciente_id)
    form = PacienteForm(request.POST or None, instance=paciente_id)
    if form.is_valid():
        paciente = form.save(commit=False)
        if not paciente.pk or request.FILES.get('foto_paciente', False):
            paciente_id.eliminar_foto_actual()
            paciente.foto_paciente = request.FILES['foto_paciente']

        cedula = form.cleaned_data.get('cedula')
        cedula = validate_clean_cedula(cedula)
        if 'cedula' in form.changed_data:
            # Si la cédula es actualizada pero ya existe un paciente del mismo
            # doctor, se debe alertar al usuario de esto
            existe_paciente = Paciente.objects.filter(cedula=cedula,
                                                      doctor=paciente.doctor)
            if existe_paciente:
                raise ValidationError(
                    "Ya uno de sus pacientes tiene la misma cédula")
        paciente.save()
        doctor_id = paciente.doctor
        msg = "%s %s con cedula %s se ha actualizado " % (
            paciente.nombres, paciente.apellidos, paciente.cedula)
        return HttpResponseRedirect("/doctor/%s" % str(doctor_id.pk))

    return render(request, "editar_paciente.html", {
        "paciente_id": paciente_id,
        "form": form,
        "doctor_id": paciente_id.doctor,
    })


def validate_clean_cedula(cedula):
    """
    Permite validar una cedula recibida como parámetro, para que cumpla
    con la siguiente estructura: V-12345678
    """
    if not re.match(r'^[vV]\-[0-9]{7,8}$', cedula):
        raise ValidationError(
            "La cédula de identidad debe contener Vv y números.")

    return cedula.upper()


def registrar_paciente(request, doctor_id):
    """
    Permite registrar un paciente para un doctor
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    form = PacienteForm(request.POST or None, request.FILES or None)
    doctor_id = get_object_or_404(Doctor, pk=doctor_id)

    # Si los datos ingresados para el paciente nuevo son válidos, se guardan
    if form.is_valid():
        p = form.save(commit=False)

        cedula = form.cleaned_data.get('cedula')
        cedula = validate_clean_cedula(cedula)
        pacientes = Paciente.objects.filter(cedula=cedula, doctor=doctor_id)

        if pacientes.count() > 0:
            raise ValidationError(
                "El paciente con C.I. %s ya existe." % cedula)
        p.doctor = doctor_id

        p.cedula = cedula
        p.foto_paciente = request.FILES['foto_paciente']
        p.nombres = form.cleaned_data.get('nombres').title()
        p.apellidos = form.cleaned_data.get('apellidos').title()
        p.email = form.cleaned_data.get('email')
        p.fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
        p.zona_residencia = form.cleaned_data.get('zona_residencia').title()
        p.estado_residencia = form.cleaned_data.get(
            'estado_residencia').title()
        p.direccion = form.cleaned_data.get('direccion')
        p.telefono_habitacion = form.cleaned_data.get('telefono_habitacion')
        p.telefono_celular = form.cleaned_data.get('telefono_celular')
        p.telefono_trabajo = form.cleaned_data.get('telefono_trabajo')
        p.consulta_medicina = form.cleaned_data.get('consulta_medicina')
        p.consulta_dermatologia = form.cleaned_data.get(
            'consulta_dermatologia')
        p.consulta_alquiler = form.cleaned_data.get('consulta_alquiler')
        p.referencia = form.cleaned_data.get('referencia')

        p.save()
        doctor = Doctor.objects.filter(username=request.user.username)
        pacientes = Paciente.objects.filter(doctor=doctor)
        msg = "%s %s con cedula %s se ha registrado " \
            "como paciente de manera exitosa" % (
                p.nombres, p.apellidos, p.cedula)
        return HttpResponseRedirect("/doctor/%s" % str(doctor_id.pk))
    context = {
        "form": form,
        "doctor_id": doctor_id
    }
    return render(request, 'registrar_paciente.html', context)


def registrar_doctor(request):
    """
    Registra un nuevo doctor en el sistema
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    form = DoctorForm(request.POST or None, request.FILES or None)
    context = {
        "form": form,
    }

    # Si los datos del doctor son válidos, el doctor es guardado en el sistema.
    if form.is_valid():
        doctor = form.save(commit=False)
        cedula = form.cleaned_data.get('cedula')
        if not re.match(r'^[vVeE]\-[0-9]{7,8}$', cedula):
            pass
        doctor.cedula = cedula
        doctor.first_name = form.cleaned_data['first_name'].title()
        doctor.last_name = form.cleaned_data['last_name'].title()
        doctor.username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        doctor.set_password(password)
        doctor.sexo = form.cleaned_data.get('sexo')
        doctor.msas = form.cleaned_data.get('msas')
        doctor.cmcs = form.cleaned_data.get('cmcs')
        doctor.save()
        msg = "Se ha registrado el(la) %s" % (doctor,)
        return HttpResponseRedirect("/?success_msg=%s" % msg)
    return render(request, 'registrar_doctor.html', context)


def iniciar_sesion(request):
    """
    Permite iniciar sesión en el sistema, consultando el usuario y clave
    ingresados por el doctor al iniciar sesión.
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                doctor = Doctor.objects.filter(user_ptr_id=request.user.id)
                pacientes = Paciente.objects.filter(doctor=doctor)
                return render(request, 'doctor_principal.html', {
                    "doctor_id": doctor[0],
                    "pacientes": pacientes,
                })
            else:
                return render(request, 'iniciar_sesion.html', {
                    'alert_msg': 'Su cuenta ha sido deshabilitada, '
                                 'Consulte al administrador del sistema'
                })
        else:
            return render(request, 'iniciar_sesion.html', {
                'error_msg': 'La cuenta no existe'
            })
    return render(request, 'iniciar_sesion.html')


def cerrar_sesion(request):
    """
    Esto permite cerrar la sesión cuando el doctor como usuario del
    sistema decide dejar de usarlo por un tiempo.
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    logout(request)
    DoctorForm(request.POST or None)
    return HttpResponseRedirect("/")


def editar_diagnostico(request, diagnostico_id):
    """
    Permite editar un diagnóstico de paciente, también se hace cargo de
    añadir, actualizar y/o eliminar las imágenes del diagnóstico según lo
    haya indicado el usuario
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    diagnostico = get_object_or_404(Diagnostico, pk=diagnostico_id)
    paciente = get_object_or_404(Paciente, pk=diagnostico.paciente.id)
    form = DiagnosticoForm(request.POST or None, request.FILES or None,
                           instance=diagnostico)
    context = {
        "form": form,
        "doctor_id": paciente.doctor,
        "paciente_id": paciente,
        "diagnostico": diagnostico,
    }

    # Si los datos del diagnóstico han sido ingresados de manera correcta,
    # se pasa a guardar los datos del diagnostico incluyendo las fotos
    if form.is_valid():
        diagnostico = form.save(commit=False)
        fotos_a_eliminar = []

        peso = form.cleaned_data.get('peso')
        estatura = form.cleaned_data.get('estatura')
        estatura /= 100
        diagnostico.imc = peso / (estatura*estatura)
        # Buscar y anotar las imágenes a borrar
        for campo, valor in request.POST.items():
            if "clear_id_" in campo:
                foto_id = int(campo.split("clear_id_")[1])
                if valor == "on":
                    fotos_a_eliminar.append(foto_id)

        # Buscar y anotar las imágenes a añadir y reemplazar
        for campo, valor in request.FILES.items():
            if not any(sufijo in campo for sufijo in
                       ["foto_diag_", "replace_id_"]):
                continue

            # Si es reemplazar, se debe anotar la actual para borrarla del
            # disco
            if "replace_id_" in campo:
                foto_id = int(campo.split("replace_id_")[1])
                fotos_a_eliminar.append(foto_id)
            diagnostico.agregar_foto(valor)

        # Si existen fotos a eliminar, eliminarlas una a una
        if fotos_a_eliminar:
            fds = FotoDiagnostico.objects.filter(pk__in=fotos_a_eliminar)
            for fd in fds:
                fd.delete()

        diagnostico.save()
        return HttpResponseRedirect("/paciente/%s" % str(paciente.pk))
    return render(request, "editar_diagnostico.html", context)


def eliminar_diagnostico(request, diagnostico_id):
    """
    Permite eliminar un diagnostico del sistema
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    diagnostico = Diagnostico.objects.get(pk=diagnostico_id)
    paciente = get_object_or_404(Paciente, pk=diagnostico.paciente.pk)
    diagnostico.delete()
    return HttpResponseRedirect("/paciente/%s" % str(paciente.pk))


def registrar_recipe(request, paciente_id):
    """
    Agrega un recipe asociado al paciente que se recibe por parámetros.
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    form = RecipeForm(request.POST or None)
    context = {
        'form': form,
        'paciente_id': paciente,
        'doctor_id': paciente.doctor,
    }

    # Si el usuario ha llenado los campos de manera exitosa, el recipe es
    # guardado
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.paciente = paciente
        recipe.save()

        return HttpResponseRedirect("/%s/recipes/" % str(paciente_id))
    return render(request, "registrar_recipe.html", context)


def editar_recipe(request, recipe_id):
    """
    Permite editar un recipe de paciente
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    paciente = get_object_or_404(Paciente, pk=recipe.paciente.id)
    form = RecipeForm(request.POST or None, instance=recipe)
    context = {
        "form": form,
        "doctor_id": paciente.doctor,
        "paciente_id": paciente,
    }

    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.save()
        return HttpResponseRedirect("/%s/recipes/" % str(paciente_id))
    return render(request, "editar_recipe.html", context)


def eliminar_recipe(request, recipe_id):
    """
    Permite eliminar un recipe del sistema
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")
    recipe = Recipe.objects.get(pk=recipe_id)
    paciente = get_object_or_404(Paciente, pk=recipe.paciente.pk)
    recipe.delete()
    return HttpResponseRedirect("/%s/recipes/" % str(paciente.pk))


def recipes_principal(request, paciente_id):
    """
    """

    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    recipes = paciente.get_recipes()
    context = {
        'paciente_id': paciente,
        "doctor_id": paciente.doctor,
        'recipes': recipes,
    }
    return render(request, "recipes_principal.html", context)


def eliminar_paciente(request, paciente_id):
    """
    Permite eliminar un paciente del sistema
    """
    # Si el usuario no ha iniciado sesión, es redirigido a la página de inicio
    # de sesión
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/iniciar_sesion/")

    paciente = Paciente.objects.get(pk=paciente_id)
    doctor = paciente.doctor
    paciente.delete()
    return HttpResponseRedirect("/doctor/%s" % str(doctor.pk))


def ver_diagnostico2 (req):
    print("los datos")
    print(req)
    print(req.FILES)
    elnombre = req.POST.get('nombre')
    print("¡Hola,", elnombre, "!")
    print(req.FILES.get('nombre'))
    img = req.FILES.get('file')

   
    
    # url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'
    url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'
    url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelUrls/'

    # data = {'file': (img), 'modelId': ('', '6df5a7eb-88fd-4b69-8455-60786f2da3c9')}
    # data = {'file': (img), 'modelId': ('', '0eb3cea3-ee96-461e-887b-3f6764a24728')}
    data = {'file': (img), 'modelId': ('', '2af34a2e-1fb8-4a85-b6ba-981195b71c85')}

    # response = requests.post(url, auth= requests.auth.HTTPBasicAuth('n0tzmZSR5d5fu5hfiSnEKL7xoGbsST5j', ''), files=data)
    # response = requests.post(url, auth= requests.auth.HTTPBasicAuth('PWUrQsIa9HMflevQIrHlKK8HtPrMcCnA', ''), files=data)
    response = requests.post(url, auth= requests.auth.HTTPBasicAuth('PWUrQsIa9HMflevQIrHlKK8HtPrMcCnA', ''), files=data)

    print(response.text)

    final = response.json()

    print(final)
    res = final['result'][0]['prediction'][0]['label']
    pro = final['result'][0]['prediction'][0]['probability']

    salida = "el resultado es: " +res+ " con una probabilidad de "+str(pro)

    res = {
        'resultado': res,
        'probabilidad': pro
    }

    # NUEVO
    return JsonResponse(res)

    # return render(req, 'salida.html', {
    #     'resultado': res,
    #     'probabilidad': pro
    # })
    # return HttpResponse(res)