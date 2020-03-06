from django.contrib import admin
from .models import Category, Institution, Team

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'key': ('name',) }
    fields = ('name', 'key', 'colour')

class TeamInline(admin.TabularInline):
    model = Team
    extra = 1
    prepopulated_fields = { 'key': ('name',) }
    readonly_fields = ('raffle',)
    fields = ('name', 'key', 'category', 'raffle')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'key': ('name',) }
    fields = ('name', 'key', 'contact_info')
    inlines = [
        TeamInline,
    ]
