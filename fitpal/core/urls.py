from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('perfil/objetivo/', views.select_objetivo, name='select_objetivo'),
    path("seleccionar-rutina/", views.seleccionar_rutina, name="seleccionar_rutina"),
    path("crear-plan/<int:rutina_id>/", views.crear_plan_desde_rutina, name="crear_plan"),
    path('plan/<int:plan_id>/', views.ver_plan, name='ver_plan'),
    path('plan/<int:plan_id>/seleccionar/', views.seleccionar_plan, name='seleccionar_plan'),
    path('plan/<int:plan_id>/log/<str:dia>/', views.registrar_progreso_dia, name='registrar_progreso'),
]
