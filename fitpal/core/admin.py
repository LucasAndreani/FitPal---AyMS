from django.contrib import admin
from .models import (
    UserProfile, 
    Amistad, 
    Logro, 
    UsuarioLogro, 
    Progreso, 
    Ejercicio, 
    PlanEntrenamiento, 
    PlanEjercicio, 
    Objetivo
)

admin.site.register(UserProfile)
admin.site.register(Amistad)
admin.site.register(Logro)
admin.site.register(UsuarioLogro)
admin.site.register(Progreso)
admin.site.register(Ejercicio)
admin.site.register(PlanEntrenamiento)
admin.site.register(PlanEjercicio)
admin.site.register(Objetivo)
