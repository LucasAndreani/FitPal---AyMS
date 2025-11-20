from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.utils import timezone
from .forms import (
    RegistroUserForm,
    PerfilForm,
    RoutineDayLogForm,
    RoutineExerciseLogForm,
)
from .models import (
    UserProfile,
    Objetivo,
    PlanEntrenamiento,
    Progreso,
    Ejercicio,
    RutinaBase,
    RutinaBaseEjercicio,
    PlanEjercicio,
    RoutineDayLog,
    RoutineExerciseLog,
)

def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = RegistroUserForm(request.POST)
        perfil_form = PerfilForm(request.POST)
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save(commit=False)
            user.email = user_form.cleaned_data.get('email')
            user.save()

            objetivo = perfil_form.cleaned_data.get('objetivo')
            if not objetivo:
                objetivo = Objetivo.objects.order_by('id').first()

            perfil = UserProfile.objects.create(
                user=user,
                edad=perfil_form.cleaned_data.get('edad'),
                peso=perfil_form.cleaned_data.get('peso'),
                altura=perfil_form.cleaned_data.get('altura'),
                objetivo=objetivo,
                nivel_experiencia=perfil_form.cleaned_data.get('nivel_experiencia') or 'beginner'
            )

            login(request, user)
            return redirect('home')
    else:
        user_form = RegistroUserForm()
        perfil_form = PerfilForm()

    return render(request, 'registro.html', {
        'user_form': user_form,
        'perfil_form': perfil_form
    })


@login_required
def home(request):
    perfil = None
    try:
        perfil = request.user.userprofile
    except UserProfile.DoesNotExist:
        perfil = UserProfile.objects.create(user=request.user)

    plan_activo = perfil.plan_actual
    ejercicios = Ejercicio.objects.all()[:10]  

    progreso_reciente = Progreso.objects.filter(usuario=request.user)\
        .select_related('ejercicio', 'day_log')\
        .order_by('-fecha')[:5]

    context = {
        'perfil': perfil,
        'plan_activo': plan_activo,
        'ejercicios': ejercicios,
        'progreso_reciente': progreso_reciente,
    }
    return render(request, 'home.html', context)


@login_required
def select_objetivo(request):
    perfil = request.user.userprofile
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'select_objetivo.html', {'form': form})


def seleccionar_rutina(request):
    rutinas = RutinaBase.objects.prefetch_related('items')
    return render(request, "seleccionar_rutina.html", {"rutinas": rutinas})

def crear_plan_desde_rutina(request, rutina_id):
    rutina = get_object_or_404(RutinaBase, id=rutina_id)

    plan = PlanEntrenamiento.objects.create(
        usuario=request.user,
        objetivo=request.user.userprofile.objetivo,
        nivel_experiencia=rutina.nivel,
        nombre=f"Plan basado en {rutina.nombre}"
    )

    ejercicios_base = RutinaBaseEjercicio.objects.filter(rutina=rutina)

    for rb in ejercicios_base:
        PlanEjercicio.objects.create(
            plan=plan,
            ejercicio=rb.ejercicio,
            series=rb.series,
            repeticiones=rb.repeticiones, 
            dia=rb.dia,
            dia_label=rb.dia_label,
        )

    return redirect("ver_plan", plan_id=plan.id)


def ver_plan(request, plan_id):
    plan = get_object_or_404(PlanEntrenamiento, id=plan_id, usuario=request.user)

    ejercicios_por_dia = {}
    for pe in PlanEjercicio.objects.filter(plan=plan).select_related('ejercicio'):
        dia = pe.dia
        if dia not in ejercicios_por_dia:
            label = pe.dia_label or pe.get_dia_display()
            ejercicios_por_dia[dia] = {"label": label, "items": []}
        ejercicios_por_dia[dia]["items"].append(pe)

    orden_dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    ejercicios_ordenados = [(d, ejercicios_por_dia[d]) for d in orden_dias if d in ejercicios_por_dia]

    logs_por_dia = {}
    for log in plan.logs.all():
        if log.dia not in logs_por_dia or log.fecha > logs_por_dia[log.dia].fecha:
            logs_por_dia[log.dia] = log

    dias = []
    for dia, data in ejercicios_ordenados:
        dias.append({
            "dia": dia,
            "label": data["label"],
            "items": data["items"],
            "ultimo_log": logs_por_dia.get(dia),
        })

    return render(request, "ver_plan.html", {
        "plan": plan,
        "dias": dias,
    })

@login_required
def seleccionar_plan(request, plan_id):
    plan = get_object_or_404(PlanEntrenamiento, id=plan_id, usuario=request.user)

    if request.method == "POST":
        perfil = request.user.userprofile
        perfil.plan_actual = plan
        perfil.save()
        return redirect('ver_plan', plan_id=plan.id)

    return redirect('ver_plan', plan_id=plan.id)


@login_required
def registrar_progreso_dia(request, plan_id, dia):
    plan = get_object_or_404(PlanEntrenamiento, id=plan_id, usuario=request.user)
    ejercicios_qs = PlanEjercicio.objects.filter(plan=plan, dia=dia).select_related('ejercicio').order_by('id')
    if not ejercicios_qs.exists():
        return redirect('ver_plan', plan_id=plan.id)
    ejercicios = list(ejercicios_qs)
    dia_label = ejercicios[0].dia_label or ejercicios[0].get_dia_display()

    RoutineExerciseLogFormSet = formset_factory(RoutineExerciseLogForm, extra=0)

    if request.method == "POST":
        day_form = RoutineDayLogForm(request.POST)
        formset = RoutineExerciseLogFormSet(request.POST, form_kwargs={'plan': plan})
        if day_form.is_valid() and formset.is_valid():
            day_log = day_form.save(commit=False)
            day_log.plan = plan
            day_log.dia = dia
            day_log.titulo = dia_label
            day_log.save()

            for form in formset:
                cd = form.cleaned_data
                if not cd:
                    continue
                log = RoutineExerciseLog.objects.create(
                    day_log=day_log,
                    plan_ejercicio=cd['plan_ejercicio'],
                    completado=cd.get('completado', False),
                    peso_usado=cd.get('peso_usado'),
                    repeticiones=cd.get('repeticiones'),
                    series=cd.get('series'),
                )
                if (
                    log.completado
                    and log.peso_usado is not None
                    and log.repeticiones is not None
                ):
                    Progreso.objects.create(
                        usuario=request.user,
                        ejercicio=log.plan_ejercicio.ejercicio,
                        day_log=day_log,
                        peso_usado=log.peso_usado,
                        repeticiones=log.repeticiones,
                    )

            return redirect('ver_plan', plan_id=plan.id)
    else:
        initial = [
            {
                'plan_ejercicio': pe.id,
                'series': pe.series,
                'repeticiones': pe.repeticiones,
            } for pe in ejercicios
        ]
        day_form = RoutineDayLogForm(initial={'fecha': timezone.now().date()})
        formset = RoutineExerciseLogFormSet(
            initial=initial,
            form_kwargs={'plan': plan},
        )

    form_pairs = list(zip(formset.forms, ejercicios))

    return render(request, "registrar_progreso.html", {
        "plan": plan,
        "dia": dia,
        "dia_label": dia_label,
        "ejercicios": ejercicios,
        "day_form": day_form,
        "formset": formset,
        "form_pairs": form_pairs,
    })