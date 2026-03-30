from django import forms
from .models import Contract, Employee, Customer

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'number', 'contract_type', 'date', 'completion_date', 'amount',
            'work_type', 'address', 'customer', 'geodesist', 'cadastral_engineer',
            'designer', 'notification', 'status', 'priority'
        ]
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите номер договора'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control address-input', 'rows': 3}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'geodesist': forms.Select(attrs={'class': 'form-select'}),
            'cadastral_engineer': forms.Select(attrs={'class': 'form-select'}),
            'designer': forms.Select(attrs={'class': 'form-select'}),
            'notification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'number': 'Номер договора',
            'contract_type': 'Вид договора',
            'date': 'Дата договора',
            'completion_date': 'Дата завершения',
            'amount': 'Сумма договора (руб.)',
            'work_type': 'Вид работ',
            'address': 'Адрес объекта работ',
            'customer': 'Заказчик',
            'geodesist': 'Геодезист',
            'cadastral_engineer': 'Кадастровый инженер',
            'designer': 'Оформление',
            'notification': 'Извещение',
            'status': 'Статус',
            'priority': 'Приоритет',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Customer, Employee
        
        self.fields['geodesist'].queryset = Employee.objects.all()
        self.fields['geodesist'].empty_label = 'Выберите геодезиста'
        self.fields['cadastral_engineer'].queryset = Employee.objects.all()
        self.fields['cadastral_engineer'].empty_label = 'Выберите инженера'
        self.fields['designer'].queryset = Employee.objects.all()
        self.fields['designer'].empty_label = 'Выберите оформителя'
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['customer'].empty_label = 'Выберите заказчика'
        self.fields['completion_date'].required = False
        
        # Простая установка дат
        if self.instance and self.instance.pk:
            if self.instance.date:
                self.initial['date'] = self.instance.date
            if self.instance.completion_date:
                self.initial['completion_date'] = self.instance.completion_date

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'position']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ФИО сотрудника'
            }),
            'position': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'full_name': 'ФИО сотрудника',
            'position': 'Должность',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Определяем выбор должностей
        POSITION_CHOICES = [
            ('', 'Выберите должность'),
            ('geodesist', 'Геодезист'),
            ('cadastral_engineer', 'Кадастровый инженер'),
            ('designer', 'Оформитель'),
            ('all', 'Универсальный специалист'),
        ]
        self.fields['position'] = forms.ChoiceField(
            choices=POSITION_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select'}),
            label='Должность',
            required=True
        )

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'inn', 'kpp', 'ogrn', 'address', 'phone', 'email', 'contact_person', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ООО "Ромашка"'
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789012'
            }),
            'kpp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789'
            }),
            'ogrn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890123'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'г. Москва, ул. Примерная, д. 1'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'info@example.ru'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Дополнительная информация'
            }),
        }
        labels = {
            'name': 'Название организации *',
            'inn': 'ИНН',
            'kpp': 'КПП',
            'ogrn': 'ОГРН',
            'address': 'Юридический адрес',
            'phone': 'Телефон',
            'email': 'Email',
            'contact_person': 'Контактное лицо',
            'is_active': 'Активен',
            'notes': 'Примечания',
        }
    
    def clean_inn(self):
        inn = self.cleaned_data.get('inn')
        if inn and len(inn) not in [10, 12]:
            raise forms.ValidationError('ИНН должен содержать 10 или 12 цифр')
        return inn
    
    def clean_ogrn(self):
        ogrn = self.cleaned_data.get('ogrn')
        if ogrn and len(ogrn) not in [13, 15]:
            raise forms.ValidationError('ОГРН должен содержать 13 или 15 цифр')
        return ogrn