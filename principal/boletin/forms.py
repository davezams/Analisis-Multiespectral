# -*- coding: utf-8 -*-
from django import forms
from .models import Doctor, Paciente, Diagnostico, Recipe


class DoctorForm(forms.ModelForm):

    """
    Formulario para el Doctor
    """
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        """
        Se establecen los nombres de los campos
        """
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['first_name'].label = 'Nombres'
        self.fields['cedula'].label = 'Cédula de Identidad'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['password'].label = 'Contraseña'
        self.fields['msas'].label = 'M.S.A.S'
        self.fields['cmcs'].label = 'C.M.C.S'

    class Meta:  # pylint: disable=C1001
        model = Doctor
        fields = [
            "username",
            "first_name",
            "last_name",
            "cedula",
            "sexo",
            "email",
            "msas",
            "cmcs",
        ]


class PacienteForm(forms.ModelForm):

    """
    Formulario para el Paciente
    """
    fecha_nacimiento = forms.DateField(
        widget=forms.widgets.DateInput(
            format="%d/%m/%Y",
            attrs={'class': 'datepicker'}
        ),
        input_formats=('%d-%m-%Y', '%d/%m/%Y', '%d/%m/%y',)
    )
    referencia = forms.CharField(widget=forms.Textarea)
    direccion = forms.CharField(widget=forms.Textarea)

    class Meta:  # pylint: disable=C1001
        model = Paciente
        fields = [
            "foto_paciente",
            "cedula",
            "nombres",
            "apellidos",
            "fecha_nacimiento",
            "zona_residencia",
            "estado_residencia",
            "direccion",
            "email",
            "telefono_habitacion",
            "telefono_celular",
            "telefono_trabajo",
            "consulta_medicina",
            "consulta_dermatologia",
            "consulta_alquiler",
            "referencia",
        ]


class DiagnosticoForm(forms.ModelForm):

    """
    Formulario para el Diagnóstico
    """
    antecedentes = forms.CharField(widget=forms.Textarea)
    examen_dermatologico = forms.CharField(widget=forms.Textarea)
    peso = forms.FloatField(widget=forms.TextInput)
    estatura = forms.FloatField(widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        """
        Se establecen los nombres de los campos
        """
        super(DiagnosticoForm, self).__init__(*args, **kwargs)
        self.fields['peso'].label = 'Peso (Kg.)'
        self.fields['estatura'].label = 'Estatura (cm.)'

    class Meta:  # pylint: disable=C1001
        model = Diagnostico
        fields = [
            "peso",
            "estatura",
            "antecedentes",
            "examen_dermatologico",
        ]


class RecipeForm(forms.ModelForm):

    """
    Formulario para los Recipes
    """
    recipe = forms.CharField(widget=forms.Textarea)
    indicaciones = forms.CharField(widget=forms.Textarea)

    class Meta:  # pylint: disable=C1001
        model = Recipe
        fields = [
            "recipe",
            "indicaciones",
        ]
