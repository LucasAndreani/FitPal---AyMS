# Proyecto FitPal – Segundo Parcial - Lucas Andreani

## Introducción

El presente documento describe el estado actual de FitPal, una aplicación web desarrollada en Django para la gestión de rutinas de entrenamiento personalizadas y el seguimiento del progreso de los usuarios. Esta segunda entrega presenta la implementación casi completa del MVP.

La aplicación fue implementada utilizando Django con SQLite como base de datos para el desarrollo local.
- **Trello**: https://trello.com/invite/b/68cf346384f0de9028980277/ATTI0ecb8d18d211ffdca518b4db1302d27aA53D4CB0/fitpal
- **GitHub**: https://github.com/LucasAndreani/FitPal---AyMS

## Estado del Proyecto

### Funcionalidades Implementadas (MVP)

- **Registrarse e iniciar sesión**: Sistema de autenticación Django con creación automática de perfil mediante signals
- **Definir objetivos y nivel**: Selección de objetivos predeterminados (Ganar masa, Subir peso, Bajar peso, Mantener, Volumen, Corte) y nivel de experiencia (Principiante, Intermedio, Avanzado)
- **Seleccionar rutinas predefinidas**: Catálogo de rutinas base (Push Pull Legs, Full Body, Tren Superior/Inferior, Bro Split) organizadas por nivel
- **Crear planes personalizados**: Clonación de rutinas base a planes de usuario
- **Visualizar rutinas activas**: Página principal con desglose por días y ejercicios
- **Registrar progreso diario**: Sistema de logging con registro de peso, repeticiones, series y ejercicios completados
- **Gestión de plan activo**: Un solo plan activo por usuario

## Story Mapping Actualizado

### Épicas Implementadas

1. **Registrarse / Iniciar Sesión**: Registro, login, logout, creación automática de perfil
2. **Definir Objetivos**: Selección y edición de objetivos y nivel de experiencia
3. **Obtener Plan de Entrenamiento**: Catálogo de rutinas, clonación a planes, visualización detallada
4. **Registrar Progreso**: Formulario dinámico por día, registro de métricas, creación de logs
5. **Revisar Progreso**: Visualización de progreso reciente y historial

### Épicas Pendientes

- **Gamificación / Recompensas**: Sistema de logros (modelos creados)
- **Gestión de Amistades**: Solicitudes y gestión de amigos (modelos creados)

## Diagrama Entidad-Relación (DER)

### Entidades Principales

- **User** (Django Auth): username, email, password
- **UserProfile**: edad, peso, altura, objetivo, nivel_experiencia, plan_actual
- **Objetivo**: nombre (6 objetivos predeterminados)
- **Ejercicio**: nombre, musculo, descripcion
- **RutinaBase**: nombre, nivel (templates de rutinas)
- **RutinaBaseEjercicio**: rutina, ejercicio, series, repeticiones, dia, dia_label
- **PlanEntrenamiento**: nombre, usuario, objetivo, nivel_experiencia, fecha_creacion
- **PlanEjercicio**: plan, ejercicio, series, repeticiones, dia, dia_label
- **RoutineDayLog**: plan, dia, fecha, titulo, notas, completado
- **RoutineExerciseLog**: day_log, plan_ejercicio, completado, peso_usado, repeticiones, series
- **Progreso**: usuario, ejercicio, fecha, peso_usado, repeticiones, day_log

### Relaciones Principales

- User ↔ UserProfile (1:1)
- UserProfile → Objetivo (N:1)
- UserProfile → PlanEntrenamiento (N:1, plan_actual)
- User → PlanEntrenamiento (1:N)
- RutinaBase ↔ Ejercicio (N:M vía RutinaBaseEjercicio)
- PlanEntrenamiento ↔ Ejercicio (N:M vía PlanEjercicio)
- PlanEntrenamiento → RoutineDayLog (1:N)
- RoutineDayLog → RoutineExerciseLog (1:N)
- User → Progreso (1:N)

## Arquitectura

### Estructura del Proyecto

```
fitpal/
├── core/                   
│   ├── models.py          
│   ├── views.py            
│   ├── forms.py           
│   ├── urls.py            
│   ├── signals.py          
│   ├── tests.py          
│   └── templates/      
├── fitpal/               
│   ├── settings.py        
│   └── urls.py
└── migrations/          
```

### Flujo de Datos

1. **Autenticación**: `/login/` o `/registro/` → Signal crea UserProfile → Redirección a `/home`
2. **Selección de Rutina**: `/seleccionar-rutina/` → Clonación a PlanEntrenamiento → `/plan/<id>/`
3. **Registro de Progreso**: `/plan/<id>/log/<dia>/` → Formset dinámico → RoutineDayLog + RoutineExerciseLog → Progreso
4. **Visualización**: `/home` muestra plan activo y últimos 5 registros de progreso

## Pruebas Unitarias

### Cobertura (17 tests)

- **ModelTests (5)**: Creación de perfiles, rutinas, planes, relaciones, herencia
- **ViewTests (6)**: Autenticación, vistas, clonación, seguridad, selección
- **ProgressLoggingTests (3)**: Logs de día, ejercicios, creación de Progreso
- **BusinessLogicTests (3)**: Ordenamiento, herencia, lógica de plan único

**Resultado**: Todos los tests pasan con exito

```bash
python manage.py test core.tests --verbosity=2
```

## Versionado

### Tags Creados

- **v1.0.0**: MVP inicializado - Sistema de rutinas y progreso funcional
- **v1.0.1**: Configuración de seguridad - Variables de entorno

Los tags están disponibles en GitHub y pueden clonarse localmente.


## Funcionalidades Pendientes

- Gestión de amistades (UI)
- Sistema de logros (gamificación)
- Estadísticas avanzadas
- Compartir rutinas
- Notificaciones
