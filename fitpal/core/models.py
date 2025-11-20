from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

NIVELES = (
    ('beginner', 'Principiante'),
    ('intermediate', 'Intermedio'),
    ('advanced', 'Avanzado'),
)

OBJETIVOS_PREDETERMINADOS = [
    ("ganar_masa", "Ganar masa muscular"),
    ("subir_peso", "Subir de peso"),
    ("bajar_peso", "Bajar de peso"),
    ("mantener", "Mantener peso"),
    ("volumen", "Volumen"),
    ("corte", "Corte"),
]

DIAS_SEMANA = [
    ("lunes", "Lunes"),
    ("martes", "Martes"),
    ("miercoles", "Miércoles"),
    ("jueves", "Jueves"),
    ("viernes", "Viernes"),
    ("sabado", "Sábado"),
    ("domingo", "Domingo"),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    edad = models.IntegerField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objetivo = models.ForeignKey('Objetivo', on_delete=models.SET_NULL, null=True, blank=True)
    nivel_experiencia = models.CharField(max_length=20, choices=NIVELES, default='beginner')

    plan_actual = models.ForeignKey(
        'PlanEntrenamiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios_con_plan"
    )

    def __str__(self):
        return self.user.username


class Objetivo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Ejercicio(models.Model):
    MUSCULOS = [
        ('pecho', 'Pecho'),
        ('espalda', 'Espalda'),
        ('piernas', 'Piernas'),
        ('hombros', 'Hombros'),
        ('biceps', 'Bíceps'),
        ('triceps', 'Tríceps'),
        ('core', 'Core'),
        ('fullbody', 'Full Body'),
    ]

    nombre = models.CharField(max_length=100)
    musculo = models.CharField(max_length=30, choices=MUSCULOS)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre



class RutinaBase(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=NIVELES, default='beginner')

    def __str__(self):
        return self.nombre

    @property
    def dia_labels(self):
        labels_por_dia = {}
        for item in self.items.all():
            label = item.dia_label or item.get_dia_display()
            if item.dia not in labels_por_dia:
                labels_por_dia[item.dia] = label

        ordered = []
        for dia_code, _ in DIAS_SEMANA:
            if dia_code in labels_por_dia:
                ordered.append(labels_por_dia[dia_code])
        return ordered


class RutinaBaseEjercicio(models.Model):
    rutina = models.ForeignKey(RutinaBase, on_delete=models.CASCADE, related_name="items")
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.IntegerField(default=3)
    repeticiones = models.CharField(max_length=20, default="10")
    dia = models.CharField(max_length=15, choices=DIAS_SEMANA)
    dia_label = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.rutina.nombre}"


class PlanEntrenamiento(models.Model):
    nombre = models.CharField(max_length=120, default="Plan personalizado")
    descripcion = models.TextField(blank=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='planes_creados'
    )

    objetivo = models.ForeignKey(Objetivo, on_delete=models.SET_NULL, null=True, blank=True)
    nivel_experiencia = models.CharField(max_length=20, choices=NIVELES, default='beginner')

    ejercicios = models.ManyToManyField(Ejercicio, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre}"


class PlanEjercicio(models.Model):
    plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.IntegerField(default=3)
    repeticiones = models.CharField(max_length=20, default="10")
    dia = models.CharField(max_length=15, choices=DIAS_SEMANA)
    dia_label = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        label = self.dia_label or self.get_dia_display()
        return f"{self.ejercicio.nombre} ({label})"


class Progreso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    day_log = models.ForeignKey('RoutineDayLog', on_delete=models.CASCADE, null=True, blank=True, related_name='entradas')
    fecha = models.DateTimeField(auto_now_add=True)
    peso_usado = models.DecimalField(max_digits=5, decimal_places=2)
    repeticiones = models.IntegerField()

    def __str__(self):
        if self.day_log and self.day_log.titulo:
            return f"{self.usuario.username} - {self.day_log.titulo} - {self.ejercicio.nombre}"
        return f"{self.usuario.username} - {self.ejercicio.nombre} ({self.fecha})"


class RoutineDayLog(models.Model):
    plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE, related_name='logs')
    dia = models.CharField(max_length=15, choices=DIAS_SEMANA)
    fecha = models.DateField(default=timezone.now)
    completado = models.BooleanField(default=False)
    notas = models.TextField(blank=True)
    titulo = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        unique_together = ('plan', 'dia', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.plan.nombre} - {self.dia} ({self.fecha})"


class RoutineExerciseLog(models.Model):
    day_log = models.ForeignKey(RoutineDayLog, on_delete=models.CASCADE, related_name='exercise_logs')
    plan_ejercicio = models.ForeignKey(PlanEjercicio, on_delete=models.CASCADE, related_name='logs')
    completado = models.BooleanField(default=False)
    peso_usado = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    repeticiones = models.IntegerField(null=True, blank=True)
    series = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.day_log} - {self.plan_ejercicio.ejercicio.nombre}"


class Amistad(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('bloqueada', 'Bloqueada'),
    )

    usuario1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amistades_enviadas')
    usuario2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amistades_recibidas')
    fecha_amistad = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"{self.usuario1.username} ↔ {self.usuario2.username} ({self.estado})"


class Logro(models.Model):
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.descripcion


class UsuarioLogro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} → {self.logro.descripcion}"
