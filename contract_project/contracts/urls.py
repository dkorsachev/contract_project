from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # Маршруты для договоров
    path('', views.ContractListView.as_view(), name='contract_list'),
    path('create/', views.contract_create, name='contract_create'),
    path('<int:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('<int:pk>/delete/', views.contract_delete, name='contract_delete'),
    
    # Маршруты для сотрудников
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/json/', views.get_customers_json, name='get_customers_json'),
    path('dashboard/', views.dashboard, name='dashboard'),
]