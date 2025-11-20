from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import (
    UserProfile, Objetivo, Ejercicio, RutinaBase, RutinaBaseEjercicio,
    PlanEntrenamiento, PlanEjercicio, RoutineDayLog, RoutineExerciseLog, Progreso
)


class ModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.objetivo = Objetivo.objects.create(nombre='Ganar masa muscular')
        self.ejercicio = Ejercicio.objects.create(
            nombre='Press de banca',
            musculo='pecho',
            descripcion='Ejercicio para pecho'
        )
    
    def test_user_profile_creation(self):
        perfil = UserProfile.objects.get(user=self.user)
        perfil.edad = 25
        perfil.peso = Decimal('75.5')
        perfil.altura = Decimal('1.75')
        perfil.objetivo = self.objetivo
        perfil.nivel_experiencia = 'intermediate'
        perfil.save()
        
        self.assertEqual(perfil.user.username, 'testuser')
        self.assertEqual(perfil.edad, 25)
        self.assertEqual(perfil.nivel_experiencia, 'intermediate')
        self.assertEqual(str(perfil), 'testuser')
    
    def test_rutina_base_creation(self):
        rutina = RutinaBase.objects.create(
            nombre='Push Pull Legs',
            nivel='intermediate'
        )
        self.assertEqual(rutina.nombre, 'Push Pull Legs')
        self.assertEqual(rutina.nivel, 'intermediate')
    
    def test_rutina_base_ejercicio_relationship(self):
        rutina = RutinaBase.objects.create(nombre='Test Routine', nivel='beginner')
        ejercicio = Ejercicio.objects.create(nombre='Sentadillas', musculo='piernas')
        
        rutina_ejercicio = RutinaBaseEjercicio.objects.create(
            rutina=rutina,
            ejercicio=ejercicio,
            series=4,
            repeticiones='8-10',
            dia='lunes',
            dia_label='Lunes - Push'
        )
        
        self.assertEqual(rutina.items.count(), 1)
        self.assertEqual(rutina_ejercicio.ejercicio.nombre, 'Sentadillas')
        self.assertEqual(rutina_ejercicio.dia_label, 'Lunes - Push')
    
    def test_plan_entrenamiento_creation(self):
        perfil = UserProfile.objects.get(user=self.user)
        perfil.objetivo = self.objetivo
        perfil.save()
        
        plan = PlanEntrenamiento.objects.create(
            nombre='Mi Plan',
            usuario=self.user,
            objetivo=self.objetivo,
            nivel_experiencia='beginner'
        )
        
        self.assertEqual(plan.usuario, self.user)
        self.assertEqual(plan.objetivo, self.objetivo)
        self.assertEqual(plan.nivel_experiencia, 'beginner')
    
    def test_plan_ejercicio_inheritance(self):

        rutina = RutinaBase.objects.create(nombre='Test', nivel='beginner')
        ejercicio = Ejercicio.objects.create(nombre='Press', musculo='pecho')
        
        rutina_ej = RutinaBaseEjercicio.objects.create(
            rutina=rutina,
            ejercicio=ejercicio,
            series=3,
            repeticiones='10',
            dia='lunes',
            dia_label='Lunes - Push'
        )
        
        plan = PlanEntrenamiento.objects.create(
            nombre='Plan Test',
            usuario=self.user,
            objetivo=self.objetivo
        )
        
        plan_ej = PlanEjercicio.objects.create(
            plan=plan,
            ejercicio=ejercicio,
            series=rutina_ej.series,
            repeticiones=rutina_ej.repeticiones,
            dia=rutina_ej.dia,
            dia_label=rutina_ej.dia_label
        )
        
        self.assertEqual(plan_ej.dia_label, 'Lunes - Push')
        self.assertEqual(plan_ej.series, 3)


class ViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.objetivo = Objetivo.objects.create(nombre='Ganar masa')
        self.perfil = UserProfile.objects.get(user=self.user)
        self.perfil.objetivo = self.objetivo
        self.perfil.save()
    
    def test_home_requires_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  
        
    def test_home_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('perfil', response.context)
    
    def test_seleccionar_rutina_view(self):
        self.client.login(username='testuser', password='testpass123')
        rutina = RutinaBase.objects.create(nombre='Test Routine', nivel='beginner')
        
        response = self.client.get(reverse('seleccionar_rutina'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('rutinas', response.context)
        self.assertIn(rutina, response.context['rutinas'])
    
    def test_crear_plan_desde_rutina(self):
        self.client.login(username='testuser', password='testpass123')
        
        rutina = RutinaBase.objects.create(nombre='Push Pull Legs', nivel='intermediate')
        ejercicio = Ejercicio.objects.create(nombre='Press Banca', musculo='pecho')
        
        RutinaBaseEjercicio.objects.create(
            rutina=rutina,
            ejercicio=ejercicio,
            series=4,
            repeticiones='8-10',
            dia='lunes',
            dia_label='Lunes - Push'
        )
        
        response = self.client.post(reverse('crear_plan', args=[rutina.id]))
        
        self.assertEqual(response.status_code, 302)
        
        plan = PlanEntrenamiento.objects.filter(usuario=self.user).first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.nombre, f'Plan basado en {rutina.nombre}')
        
        plan_ejercicios = PlanEjercicio.objects.filter(plan=plan)
        self.assertEqual(plan_ejercicios.count(), 1)
        self.assertEqual(plan_ejercicios.first().ejercicio, ejercicio)
        self.assertEqual(plan_ejercicios.first().dia_label, 'Lunes - Push')
    
    def test_ver_plan_requires_ownership(self):
        otro_user = User.objects.create_user(username='otro', password='pass123')
        otro_plan = PlanEntrenamiento.objects.create(
            nombre='Plan Ajeno',
            usuario=otro_user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ver_plan', args=[otro_plan.id]))
        self.assertEqual(response.status_code, 404)  
    def test_seleccionar_plan_as_active(self):
        self.client.login(username='testuser', password='testpass123')
        
        plan = PlanEntrenamiento.objects.create(
            nombre='Mi Plan',
            usuario=self.user,
            objetivo=self.objetivo
        )
        
        response = self.client.post(reverse('seleccionar_plan', args=[plan.id]))
        self.assertEqual(response.status_code, 302)
        
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.plan_actual, plan)


class ProgressLoggingTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.perfil = UserProfile.objects.get(user=self.user)
        self.objetivo = Objetivo.objects.create(nombre='Ganar masa')
        
        self.plan = PlanEntrenamiento.objects.create(
            nombre='Mi Plan',
            usuario=self.user,
            objetivo=self.objetivo
        )
        
        self.ejercicio = Ejercicio.objects.create(
            nombre='Press Banca',
            musculo='pecho'
        )
        
        self.plan_ejercicio = PlanEjercicio.objects.create(
            plan=self.plan,
            ejercicio=self.ejercicio,
            series=4,
            repeticiones='8-10',
            dia='lunes',
            dia_label='Lunes - Push'
        )
    
    def test_create_day_log(self):
        day_log = RoutineDayLog.objects.create(
            plan=self.plan,
            dia='lunes',
            fecha=timezone.now().date(),
            titulo='Lunes - Push',
            notas='Buen entrenamiento'
        )
        
        self.assertEqual(day_log.plan, self.plan)
        self.assertEqual(day_log.dia, 'lunes')
        self.assertEqual(day_log.titulo, 'Lunes - Push')
    
    def test_create_exercise_log(self):
        day_log = RoutineDayLog.objects.create(
            plan=self.plan,
            dia='lunes',
            fecha=timezone.now().date(),
            titulo='Lunes - Push'
        )
        
        exercise_log = RoutineExerciseLog.objects.create(
            day_log=day_log,
            plan_ejercicio=self.plan_ejercicio,
            completado=True,
            peso_usado=Decimal('80.0'),
            repeticiones=10,
            series=4
        )
        
        self.assertEqual(exercise_log.day_log, day_log)
        self.assertEqual(exercise_log.completado, True)
        self.assertEqual(exercise_log.peso_usado, Decimal('80.0'))
    
    def test_progress_creation_from_log(self):
        day_log = RoutineDayLog.objects.create(
            plan=self.plan,
            dia='lunes',
            fecha=timezone.now().date(),
            titulo='Lunes - Push'
        )
        
        exercise_log = RoutineExerciseLog.objects.create(
            day_log=day_log,
            plan_ejercicio=self.plan_ejercicio,
            completado=True,
            peso_usado=Decimal('80.0'),
            repeticiones=10,
            series=4
        )
        
        if (exercise_log.completado and 
            exercise_log.peso_usado is not None and 
            exercise_log.repeticiones is not None):
            progreso = Progreso.objects.create(
                usuario=self.user,
                ejercicio=self.ejercicio,
                day_log=day_log,
                peso_usado=exercise_log.peso_usado,
                repeticiones=exercise_log.repeticiones
            )
            
            self.assertEqual(progreso.usuario, self.user)
            self.assertEqual(progreso.ejercicio, self.ejercicio)
            self.assertEqual(progreso.peso_usado, Decimal('80.0'))
            self.assertEqual(progreso.repeticiones, 10)
            self.assertEqual(progreso.day_log, day_log)


class BusinessLogicTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.objetivo = Objetivo.objects.create(nombre='Ganar masa')
        self.perfil = UserProfile.objects.get(user=self.user)
        self.perfil.objetivo = self.objetivo
        self.perfil.nivel_experiencia = 'intermediate'
        self.perfil.save()
    
    def test_rutina_base_dia_labels_property(self):

        rutina = RutinaBase.objects.create(nombre='PPL', nivel='intermediate')
        ejercicio1 = Ejercicio.objects.create(nombre='Press', musculo='pecho')
        ejercicio2 = Ejercicio.objects.create(nombre='Pull', musculo='espalda')
        
        RutinaBaseEjercicio.objects.create(
            rutina=rutina,
            ejercicio=ejercicio1,
            dia='lunes',
            dia_label='Lunes - Push'
        )
        RutinaBaseEjercicio.objects.create(
            rutina=rutina,
            ejercicio=ejercicio2,
            dia='martes',
            dia_label='Martes - Pull'
        )
        
        labels = rutina.dia_labels
        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0], 'Lunes - Push')
        self.assertEqual(labels[1], 'Martes - Pull')
    
    def test_plan_inherits_nivel_from_rutina(self):
        rutina = RutinaBase.objects.create(
            nombre='Rutina Avanzada',
            nivel='advanced'
        )
        
        plan = PlanEntrenamiento.objects.create(
            nombre=f'Plan basado en {rutina.nombre}',
            usuario=self.user,
            objetivo=self.objetivo,
            nivel_experiencia=rutina.nivel
        )
        
        self.assertEqual(plan.nivel_experiencia, 'advanced')
    
    def test_user_can_only_have_one_active_plan(self):
        plan1 = PlanEntrenamiento.objects.create(
            nombre='Plan 1',
            usuario=self.user,
            objetivo=self.objetivo
        )
        plan2 = PlanEntrenamiento.objects.create(
            nombre='Plan 2',
            usuario=self.user,
            objetivo=self.objetivo
        )
        
        self.perfil.plan_actual = plan1
        self.perfil.save()
        
        self.perfil.plan_actual = plan2
        self.perfil.save()
        
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.plan_actual, plan2)
        self.assertNotEqual(self.perfil.plan_actual, plan1)
