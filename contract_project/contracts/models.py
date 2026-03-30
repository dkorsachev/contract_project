from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Customer(models.Model):
    """Модель заказчика"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Название организации')
    inn = models.CharField(max_length=12, blank=True, verbose_name='ИНН')
    kpp = models.CharField(max_length=9, blank=True, verbose_name='КПП')
    ogrn = models.CharField(max_length=13, blank=True, verbose_name='ОГРН')
    address = models.TextField(blank=True, verbose_name='Юридический адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='Контактное лицо')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """Модель сотрудника (геодезист, инженер, оформитель)"""
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Contract(models.Model):
    # Типы договоров
    CONTRACT_TYPES = [
        ('contract', 'Договор'),
        ('subcontract', 'Договор подряда'),
        ('contract_work', 'Контракт'),
    ]

    # Виды работ
    WORK_TYPES = [
        ('land_survey', 'Межевой план'),
        ('technical_plan', 'Технический план'),
        ('kp_diagram', 'Схема на КПТ'),
    ]

    # Статусы
    STATUS_CHOICES = [
        ('in_progress', 'В работе'),
        ('completed', 'Выполнено'),
        ('finished', 'Завершено'),
        ('suspended', 'Приостановлено'),
    ]

    # Приоритеты
    PRIORITY_CHOICES = [
        ('relax', 'Расслабься'),
        ('normal', 'Нормальный'),
        ('urgent', 'Срочный'),
        ('critical', 'Критический'),
    ]

    # Заказчики (встроенный словарь)
    CUSTOMER_CHOICES = [
        ('customer1', 'ООО "Ромашка"'),
        ('customer2', 'ИП Петров'),
        ('customer3', 'АО "СтройИнвест"'),
        ('customer4', 'ООО "ГеоПроект"'),
        ('customer5', 'ФГБУ "Кадастр"'),
    ]

    # Основные поля
    number = models.CharField(max_length=50, unique=True, verbose_name='Номер договора')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, verbose_name='Вид договора')
    date = models.DateField(verbose_name='Дата договора')
    completion_date = models.DateField(null=True, blank=True, verbose_name='Дата завершения')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма договора')
    work_type = models.CharField(max_length=20, choices=WORK_TYPES, verbose_name='Вид работ')
    address = models.TextField(verbose_name='Адрес объекта работ')
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT, 
        verbose_name='Заказчик',
        related_name='contracts'
    )
    geodesist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='geodesist_contracts', verbose_name='Геодезист')
    cadastral_engineer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='cadastral_contracts', verbose_name='Кадастровый инженер')
    designer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='designer_contracts', verbose_name='Оформление')
    notification = models.TextField(blank=True, verbose_name='Извещение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name='Приоритет')

    # Аудиторские поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменён')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts', verbose_name='Создал')

    # История изменений (django-simple-history)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.number} - {self.customer}"

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
        ordering = ['-date']


