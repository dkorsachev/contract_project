from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.template.loader import render_to_string  # ← ДОБАВИТЬ ЭТОТ ИМПОРТ
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth, TruncWeek
from .models import Contract, Employee, Customer
from .forms import ContractForm, EmployeeForm, CustomerForm
import calendar, json
from django.core.cache import cache


class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'contracts/index.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(number__icontains=q) |
                Q(contract_type__icontains=q) |
                Q(work_type__icontains=q) |
                Q(address__icontains=q) |
                Q(customer__name__icontains=q) |
                Q(work_description__icontains=q) |
                Q(status__icontains=q) |
                Q(priority__icontains=q) |
                Q(geodesist__full_name__icontains=q) |
                Q(cadastral_engineer__full_name__icontains=q) |
                Q(designer__full_name__icontains=q)
            )
            return queryset
        
        # Фильтры по сотрудникам
        geodesist_id = self.request.GET.get('geodesist')
        if geodesist_id:
            queryset = queryset.filter(geodesist_id=geodesist_id)
        
        engineer_id = self.request.GET.get('cadastral_engineer')
        if engineer_id:
            queryset = queryset.filter(cadastral_engineer_id=engineer_id)
        
        designer_id = self.request.GET.get('designer')
        if designer_id:
            queryset = queryset.filter(designer_id=designer_id)
        
        # Фильтры по статусу и приоритету
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем отфильтрованный queryset для статистики
        filtered_queryset = self.get_queryset()
        
        # Общая сумма отфильтрованных договоров
        total_sum = filtered_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Сумма выполненных в отфильтрованном списке
        completed_sum = filtered_queryset.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Статистика по статусам для отфильтрованного списка
        status_stats = {}
        for status_code, status_name in Contract.STATUS_CHOICES:
            status_stats[status_code] = {
                'name': status_name,
                'count': filtered_queryset.filter(status=status_code).count(),
                'sum': filtered_queryset.filter(status=status_code).aggregate(total=Sum('amount'))['total'] or 0
            }
        
        context['search_query'] = self.request.GET.get('q', '')
        context['priority_colors'] = {
            'relax': 'success',
            'normal': 'primary',
            'urgent': 'warning',
            'critical': 'danger',
        }
        context['total_sum'] = total_sum
        context['completed_sum'] = completed_sum
        context['status_stats'] = status_stats
        
        # Передаем выбранные значения фильтров для сохранения в форме
        context['selected_geodesist'] = self.request.GET.get('geodesist', '')
        context['selected_engineer'] = self.request.GET.get('cadastral_engineer', '')
        context['selected_designer'] = self.request.GET.get('designer', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_priority'] = self.request.GET.get('priority', '')
        
        # Списки для выпадающих списков
        from .models import Employee
        context['geodesists'] = Employee.objects.filter(position='geodesist')
        context['engineers'] = Employee.objects.filter(position='cadastral_engineer')
        context['designers'] = Employee.objects.filter(position='designer')
        
        return context
  

@login_required
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()
            
            # Проверяем AJAX запрос
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('contracts:contract_list')
        else:
            # Если форма не валидна и это AJAX запрос, возвращаем форму с ошибками
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('contracts/contract_form_modal.html', {
                    'form': form,
                    'title': 'Создание договора'
                }, request=request)
                return JsonResponse({'status': 'error', 'html': html})
    else:
        form = ContractForm()
    
    # GET запрос - возвращаем форму
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/contract_form_modal.html', {
            'form': form,
            'title': 'Создание договора'
        })
    return render(request, 'contracts/contract_form.html', {'form': form})


@login_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    
    # Отладка: выводим даты в консоль
    print(f"=== Редактирование договора {pk} ===")
    print(f"Дата договора: {contract.date}")
    print(f"Дата завершения: {contract.completion_date}")
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('contracts:contract_list')
    else:
        form = ContractForm(instance=contract)
        
        # Проверяем, что даты попали в форму
        print(f"Initial date: {form.initial.get('date')}")
        print(f"Initial completion_date: {form.initial.get('completion_date')}")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/contract_form_modal.html', {
            'form': form,
            'title': 'Редактирование договора'
        })
    return render(request, 'contracts/contract_form.html', {'form': form})


@login_required
def contract_delete(request, pk):
    """Удаление договора"""
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        # Сохраняем номер договора для сообщения
        contract_number = contract.number
        contract.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'Договор {contract_number} удален'})
        return redirect('contracts:contract_list')
    
    # GET запрос - показываем форму подтверждения
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/contract_confirm_delete_modal.html', {'contract': contract})
    
    return render(request, 'contracts/contract_confirm_delete.html', {'contract': contract})


@login_required
def employee_list(request):
    """Список сотрудников"""
    employees = Employee.objects.all()
    search_query = request.GET.get('q', '')
    
    if search_query:
        employees = employees.filter(
            Q(full_name__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'contracts/employee_list.html', context)


@login_required
def employee_create(request):
    """Создание сотрудника"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'id': employee.id, 'name': employee.full_name})
            return redirect('contracts:employee_list')
    else:
        form = EmployeeForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/employee_form_modal.html', {
            'form': form,
            'title': 'Добавить сотрудника'
        })
    return render(request, 'contracts/employee_form.html', {'form': form})


@login_required
def employee_edit(request, pk):
    """Редактирование сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('contracts:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/employee_form_modal.html', {
            'form': form,
            'title': 'Редактировать сотрудника'
        })
    return render(request, 'contracts/employee_form.html', {'form': form})


@login_required
def employee_delete(request, pk):
    """Удаление сотрудника"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect('contracts:employee_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/employee_confirm_delete_modal.html', {'employee': employee})
    return render(request, 'contracts/employee_confirm_delete.html', {'employee': employee})

@login_required
def customer_list(request):
    """Список заказчиков"""
    customers = Customer.objects.all()
    search_query = request.GET.get('q', '')
    
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(inn__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'contracts/customer_list.html', context)


@login_required
def customer_create(request):
    """Создание заказчика"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            # Для AJAX запроса из модального окна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'id': customer.id, 'name': customer.name})
            return redirect('contracts:customer_list')
    else:
        form = CustomerForm()
    
    # Для AJAX запросов возвращаем форму для модального окна
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/customer_form_modal.html', {'form': form})
    
    # Для обычных запросов используем полную страницу
    return render(request, 'contracts/customer_form_simple.html', {'form': form})


@login_required
def customer_edit(request, pk):
    """Редактирование заказчика"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('contracts:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    # Проверяем, AJAX ли это запрос (из модального окна)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/customer_form_modal.html', {
            'form': form,
            'title': 'Редактировать заказчика'
        })
    
    # Для обычных запросов используем полную страницу
    return render(request, 'contracts/customer_form_simple.html', {
        'form': form,
        'customer': customer,
        'title': 'Редактировать заказчика'
    })


@login_required
def customer_delete(request, pk):
    """Удаление заказчика"""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Проверяем, есть ли договоры у этого заказчика
    if customer.contracts.exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error', 
                'message': 'Нельзя удалить заказчика, так как есть связанные договоры'
            })
        return redirect('contracts:customer_list')
    
    if request.method == 'POST':
        customer.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect('contracts:customer_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'contracts/customer_confirm_delete_modal.html', {'customer': customer})
    return render(request, 'contracts/customer_confirm_delete.html', {'customer': customer})

@login_required
def get_customers_json(request):
    """Возвращает список заказчиков в JSON формате"""
    customers = Customer.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse({'customers': list(customers)})

@login_required
def dashboard(request):
    """Страница дашборда с аналитикой"""
    
    # Основные статистики
    total_contracts = Contract.objects.count()
    total_amount = Contract.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Статистика по статусам
    status_stats = []
    status_colors = {
        'completed': '#28a745',
        'in_progress': '#ffc107',
        'finished': '#17a2b8',
        'suspended': '#dc3545'
    }
    
    for status_code, status_name in Contract.STATUS_CHOICES:
        count = Contract.objects.filter(status=status_code).count()
        amount = Contract.objects.filter(status=status_code).aggregate(total=Sum('amount'))['total'] or 0
        status_stats.append({
            'code': status_code,
            'name': status_name,
            'count': count,
            'amount': float(amount),
            'color': status_colors.get(status_code, '#6c757d')
        })
    
    # Статистика по приоритетам
    priority_stats = []
    priority_colors = {
        'relax': '#28a745',
        'normal': '#007bff',
        'urgent': '#ffc107',
        'critical': '#dc3545'
    }
    
    for priority_code, priority_name in Contract.PRIORITY_CHOICES:
        count = Contract.objects.filter(priority=priority_code).count()
        amount = Contract.objects.filter(priority=priority_code).aggregate(total=Sum('amount'))['total'] or 0
        priority_stats.append({
            'code': priority_code,
            'name': priority_name,
            'count': count,
            'amount': float(amount),
            'color': priority_colors.get(priority_code, '#6c757d')
        })
    
    # Статистика по месяцам (последние 6 месяцев)
    today = timezone.now().date()
    months_data = []
    
    for i in range(5, -1, -1):
        # Вычисляем месяц
        month_date = today.replace(day=1) - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        
        # Вычисляем конец месяца
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1) - timedelta(days=1)
        
        contracts = Contract.objects.filter(date__gte=month_start, date__lte=month_end)
        months_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': contracts.count(),
            'amount': float(contracts.aggregate(total=Sum('amount'))['total'] or 0)
        })
    
    # Статистика по видам работ
    work_type_stats = []
    work_type_colors = ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14']
    
    for idx, (work_code, work_name) in enumerate(Contract.WORK_TYPES):
        count = Contract.objects.filter(work_type=work_code).count()
        amount = Contract.objects.filter(work_type=work_code).aggregate(total=Sum('amount'))['total'] or 0
        work_type_stats.append({
            'code': work_code,
            'name': work_name,
            'count': count,
            'amount': float(amount),
            'color': work_type_colors[idx % len(work_type_colors)]
        })
    
    # Топ заказчиков
    top_customers = Contract.objects.values('customer__name').annotate(
        total_amount=Sum('amount'),
        contract_count=Count('id')
    ).filter(customer__isnull=False, total_amount__gt=0).order_by('-total_amount')[:10]
    
    # Преобразуем Decimal в float для JSON
    for customer in top_customers:
        customer['total_amount'] = float(customer['total_amount']) if customer['total_amount'] else 0
    
    context = {
        'total_contracts': total_contracts,
        'total_amount': float(total_amount),
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'months_data': months_data,
        'work_type_stats': work_type_stats,
        'top_customers': list(top_customers),
        # Для JSON в шаблоне
        'status_stats_json': json.dumps(status_stats),
        'priority_stats_json': json.dumps(priority_stats),
        'months_data_json': json.dumps(months_data),
        'work_type_stats_json': json.dumps(work_type_stats),
    }
    
    return render(request, 'contracts/dashboard.html', context)