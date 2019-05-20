# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import os


class Doctor(User):

    """
    Es la representación del Doctor en el sistema, basándose en el modelo
    Usuario de django con el fin el doctor pueda ser un usuario del sistema
    y pueda iniciar sesión.
    """

    cedula = models.CharField(max_length=10)
    LISTA_SEXO = (
        ('f', 'Femenino'),
        ('m', 'Masculino'),
    )
    sexo = models.CharField(
        default=LISTA_SEXO[0][0], choices=LISTA_SEXO, max_length=1)
    creado = models.DateTimeField(auto_now_add=True, auto_now=False)
    actualizado = models.DateTimeField(auto_now_add=False, auto_now=True)
    msas = models.CharField(max_length=8)
    cmcs = models.CharField(max_length=8)

    def get_etiqueta(self):
        """
        Permite tener el titulo de la página principal del doctor, basandose en
        el sexo del doctor para establecerlo en la plantilla
        """

        conector = "del " if self.sexo == "m" else "de la "
        nombre_doctor = self.get_titulo() + " " + self.last_name
        return "Pacientes " + conector + nombre_doctor

    def get_titulo(self):
        """
        Si el sexo del doctor es Masculino, usar "Dr."
        en caso contrario "Dra."
        """
        return 'Dr.' if self.sexo == 'm' else 'Dra.'

    def __unicode__(self):
        """
        Cuando un Doctor es listado en la página admin/, este método es
        llamado para mostrar datos como referencia (como una etiqueta)
        """
        return u"%s %s" % (self.get_titulo(), self.last_name)


class Paciente(models.Model):

    """
    Es la representación con datos básicos de un paciente, al cual se
    le realizan diagnósticos y puede ser creado, modificado y eliminado por
    el doctor
    """

    # Estado de Venezuela
    ESTADOS = [
        ('1', 'Amazonas'),
        ('2', 'Anzoátegui'),
        ('3', 'Apure'),
        ('4', 'Aragua'),
        ('5', 'Barinas'),
        ('6', 'Bolívar'),
        ('7', 'Carabobo'),
        ('8', 'Cojedes'),
        ('9', 'Delta Amacuro'),
        ('10', 'Falcón'),
        ('11', 'Guárico'),
        ('12', 'Lara'),
        ('13', 'Mérida'),
        ('14', 'Miranda'),
        ('15', 'Monagas'),
        ('16', 'Nueva Esparta'),
        ('17', 'Portuguesa'),
        ('18', 'Sucre'),
        ('19', 'Táchira'),
        ('20', 'Trujillo'),
        ('21', 'Vargas'),
        ('22', 'Yaracuy'),
        ('23', 'Zulia'),
        ('24', 'Distrito Capital'),
        ('25', 'Dependencias Federales'),
    ]
    foto_paciente = models.FileField("Foto")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    creado = models.DateTimeField(auto_now_add=True, auto_now=False)
    actualizado = models.DateTimeField(auto_now_add=False, auto_now=True)
    cedula = models.CharField("Cédula", max_length=10)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    email = models.EmailField("Correo Electrónico")
    fecha_nacimiento = models.DateField("Fecha de Nacimiento")
    zona_residencia = models.CharField("Zona Domicilio", max_length=120)
    estado_residencia = models.CharField("Estado Domicilio",
                                         default=ESTADOS[0][0],
                                         choices=ESTADOS, max_length=2)
    direccion = models.CharField("Dirección", max_length=500)
    telefono_habitacion = models.CharField("Teléfono Habitación", blank=True,
                                           default=None, max_length=11)
    telefono_celular = models.CharField("Teléfono Celular", blank=True,
                                        default=None, max_length=11)
    telefono_trabajo = models.CharField("Teléfono Trabajo", blank=True,
                                        default=None, max_length=11)
    consulta_medicina = models.BooleanField("Consulta por Medicinas",
                                            default=False)
    consulta_dermatologia = models.BooleanField("Consulta Dermatológica",
                                                default=False)
    consulta_alquiler = models.BooleanField("Consulta por alquiler",
                                            default=False)
    referencia = models.CharField(max_length=500, default=None)

    def __unicode__(self):
        """
        Cuando un Paciente es listado en la página admin/, este método es
        llamado para mostrar datos como referencia (como una etiqueta)
        """
        return u"%s - %s" % (self.doctor, self.nombres)

    def get_diagnosticos(self):
        """
        Devuelve los diagnósticos de un paciente acompañado de un índice y
        ordenados de manera decreciente usando la fecha de creación de cada
        uno de los diagnósticos para organizarlos.
        """
        diagnosticos = Diagnostico.objects.filter(
            paciente=self).order_by('-creado')
        return [(i+1, d) for i, d in enumerate(diagnosticos)]

    def get_recipes(self):
        """
        """
        recipes = Recipe.objects.filter(
            paciente=self).order_by('-creado')
        return [(i+1, d) for i, d in enumerate(recipes)]

    def eliminar_foto_actual(self):
        """
        Permite eliminar la foto actual del paciente del disco, esto es usado
        para cuando se decide eliminar o cambiar la foto del paciente
        """
        if os.path.isfile(self.foto_paciente.path):
            os.remove(self.foto_paciente.path)

    def delete(self, *args, **kwargs):
        """
        Cuando un paciente es eliminado, la foto del paciente es eliminada
        del disco al igual que sus diagnósticos.
        """
        self.eliminar_foto_actual()
        for i, d in self.get_diagnosticos():
            d.delete()
        super(Paciente, self).delete(*args, **kwargs)


class Recipe(models.Model):

    """
    Permite llevar los recipes de un paciente basado en recipes e indicaciones
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True, auto_now=False)
    recipe = models.CharField(max_length=500)
    indicaciones = models.CharField(max_length=500)


class Diagnostico(models.Model):

    """
    Permite llevar un diagnostico de un paciente basado en antecedentes
    y exámenes dermatológicos realizados.
    """
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True, auto_now=False)
    antecedentes = models.CharField(max_length=500)
    examen_dermatologico = models.CharField(max_length=500)
    peso = models.FloatField(default=0)
    estatura = models.FloatField(default=0)
    imc = models.FloatField(default=0)

    def get_fotos(self):
        """
        Devuelve las fotos del diagnostico realizado
        """
        return FotoDiagnostico.objects.filter(diagnostico=self.pk) or []

    def get_fotos_con_indice(self):
        """
        Devuelve las fotos del diagnóstico realizado con
        un índice para poder usarlas de manera ordenada en la plantilla
        """
        return [(i + 1, f) for i, f in enumerate(self.get_fotos())]

    def get_headline(self):
        """
        Permite mostrar un extracto de los antecedentes como título de
        cada uno de los diagnósticos mostrados
        """
        length_reached = len(self.antecedentes) > 50
        antecedentes = self.antecedentes[0:50] + "..."
        return length_reached and antecedentes or self.antecedentes

    def agregar_foto(self, foto):
        """
        Agrega una foto asociándola al diagnostico
        """
        diccionario = {
            'diagnostico': self,
            'foto': foto,
        }
        fd = FotoDiagnostico(**diccionario)
        fd.save()

    def delete(self, *args, **kwargs):
        """
        Cuando un diagnostico es eliminado por el doctor se eliminan las fotos
        del diagnostico relacionadas
        """
        for fd in self.get_fotos():
            fd.delete()

        super(Diagnostico, self).delete(*args, **kwargs)


class FotoDiagnostico(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE)
    foto = models.FileField(upload_to="photos/")

    def delete(self, *args, **kwargs):
        """
        Eliminar la foto cuando el registro FotoDiagnostico ha sido eliminado.
        """
        if os.path.isfile(self.foto.path):
            os.remove(self.foto.path)

        super(FotoDiagnostico, self).delete(*args, **kwargs)
