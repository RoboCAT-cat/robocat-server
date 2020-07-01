from django.contrib import admin
from .models import Category, Institution, Team, TeamMembership

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'key': ('name',) }
    fields = ('name', 'key', 'colour')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'key': ('name',) }
    fields = ('name', 'key', 'contact_info')
    search_fields = ('name', 'key')

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    autocomplete_fields = ('user',)
    fields = ('user',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('name', 'key', 'category', 'institution', 'raffle')
    readonly_fields = ('raffle',)
    prepopulated_fields = { 'key': ('name',) }
    autocomplete_fields = ('institution',)
    search_fields = ('name', 'key', 'members__user__username__exact')
    list_filter = ('category', ('institution', admin.RelatedOnlyFieldListFilter))
    list_display = ('name', 'category', 'institution')
    inlines = [
        TeamMembershipInline
    ]
