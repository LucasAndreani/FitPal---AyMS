# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    PlanEntrenamiento,
    PlanEjercicio,
    Progreso,
    Ejercicio,
    UserProfile,
    RoutineDayLog,
    RoutineExerciseLog,
)

class RegistroUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("edad", "peso", "altura", "objetivo", "nivel_experiencia")
        widgets = {
            "edad": forms.NumberInput(attrs={"min": 0}),
            "peso": forms.NumberInput(attrs={"step": "0.01"}),
            "altura": forms.NumberInput(attrs={"step": "0.01"}),
        }


class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['nombre', 'musculo']

class PlanForm(forms.ModelForm):
    class Meta:
        model = PlanEntrenamiento
        fields = ['objetivo']

class PlanEjercicioForm(forms.ModelForm):
    class Meta:
        model = PlanEjercicio
        fields = ['ejercicio', 'series', 'repeticiones']

class ProgresoForm(forms.ModelForm):
    class Meta:
        model = Progreso
        fields = ['ejercicio', 'peso_usado', 'repeticiones']


class RoutineDayLogForm(forms.ModelForm):
    class Meta:
        model = RoutineDayLog
        fields = ['fecha', 'completado', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }


class RoutineExerciseLogForm(forms.Form):
    plan_ejercicio = forms.ModelChoiceField(
        queryset=PlanEjercicio.objects.none(),
        widget=forms.HiddenInput
    )
    completado = forms.BooleanField(required=False)
    peso_usado = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    repeticiones = forms.IntegerField(required=False)
    series = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        plan = kwargs.pop('plan', None)
        super().__init__(*args, **kwargs)
        if plan is not None:
            self.fields['plan_ejercicio'].queryset = PlanEjercicio.objects.filter(plan=plan)
