# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # /
    url(r'^$', views.inicio, name='inicio'),

    url(r'^iniciar_sesion/$', views.iniciar_sesion, name='iniciar_sesion'),
    url(r'^cerrar_sesion/$', views.cerrar_sesion, name='cerrar_sesion'),

    # Registrar doctor
    # doctor/crear
    url(r'^doctor/crear/$', views.registrar_doctor,
        name='registrar_doctor'),

    url(r'^doctor/diagnostico2/$', views.ver_diagnostico2,
        name='ver_diagnostico2'),

    # Editar doctor
    # doctor/1/editar
    url(r'^doctor/(?P<doctor_id>[0-9]+)/editar/$', views.editar_doctor,
        name='editar_doctor'),

    url(r'^doctor/(?P<doctor_id>[0-9]+)/diagnostico/$', views.ver_diagnostico,
        name='ver_diagnostico'),

    # doctor/1
    url(r'^doctor/(?P<doctor_id>[0-9]+)/$', views.doctor_principal,
        name='doctor_principal'),

    # Agregar Paciente
    # 1/paciente/crear
    url(r'^(?P<doctor_id>[0-9]+)/paciente/crear/$', views.registrar_paciente,
        name='registrar_paciente'),

    # Ver diagnosticos de paciente
    # paciente/1/
    url(r'^paciente/(?P<paciente_id>[0-9]+)/$', views.paciente_principal,
        name='paciente_principal'),

    # Editar paciente
    # paciente/1/editar
    url(r'^paciente/(?P<paciente_id>[0-9]+)/editar/$', views.editar_paciente,
        name='editar_paciente'),

    # Eliminar paciente
    # paciente/1/eliminar/
    url(r'^paciente/(?P<paciente_id>[0-9]+)/eliminar/$',
        views.eliminar_paciente, name='eliminar_paciente'),

    # Agregar diagnostico
    # 1/diagnostico/crear/
    url(r'^(?P<paciente_id>[0-9]+)/diagnostico/crear/$',
        views.agregar_diagnostico, name='agregar_diagnostico'),

    # Editar diagnostico
    # diagnostico/1/
    url(r'^diagnostico/(?P<diagnostico_id>[0-9]+)/editar/$',
        views.editar_diagnostico, name='editar_diagnostico'),

    # Eliminar diagnostico
    # diagnostico/1/eliminar/
    url(r'^diagnostico/(?P<diagnostico_id>[0-9]+)/eliminar/$',
        views.eliminar_diagnostico, name='eliminar_diagnostico'),

    # Recipe principal
    # 1/recipes/
    url(r'^(?P<paciente_id>[0-9]+)/recipes/$',
        views.recipes_principal, name='recipes_principal'),

    # Agregar recipe
    # 1/recipe/crear/
    url(r'^(?P<paciente_id>[0-9]+)/recipe/crear/$',
        views.registrar_recipe, name='registrar_recipe'),

    # Editar recipe
    # recipe/1/
    url(r'^recipe/(?P<recipe_id>[0-9]+)/editar/$',
        views.editar_recipe, name='editar_recipe'),

    # Eliminar recipe
    # recipe/1/eliminar/
    url(r'^recipe/(?P<recipe_id>[0-9]+)/eliminar/$',
        views.eliminar_recipe, name='eliminar_recipe'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
