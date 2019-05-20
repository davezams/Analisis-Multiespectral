# -*- coding: utf-8 -*-
from django.contrib import admin
from .forms import DoctorForm, PacienteForm
from .models import Doctor, Paciente


class AdminDoctor(admin.ModelAdmin):
    list_display = ["__unicode__", "email", "creado", "actualizado"]
    form = DoctorForm

class AdminPaciente(admin.ModelAdmin):
    list_display = ["__unicode__", "fecha_nacimiento", "cedula", "foto_paciente"]
    form = PacienteForm

admin.site.register(Doctor, AdminDoctor)
admin.site.register(Paciente, AdminPaciente)
