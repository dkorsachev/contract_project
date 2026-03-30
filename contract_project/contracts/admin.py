from django.contrib import admin
from .models import Employee, Contract
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'user']
    list_filter = ['position']
    search_fields = ['full_name', 'position']
    fields = ['full_name', 'position', 'user']
    
@admin.register(Contract)
class ContractAdmin(SimpleHistoryAdmin):
    list_display = ['number', 'customer', 'status', 'priority', 'date']
    list_filter = ['status', 'priority', 'contract_type']
    search_fields = ['number', 'customer', 'address']