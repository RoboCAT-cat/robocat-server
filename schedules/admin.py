from django.contrib import admin
from django.utils.translation import (gettext as _, gettext_lazy, ngettext)
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponseRedirect
from django.db import transaction
from .models import Schedule, ScheduledMatch

class ScheduledMatchInline(admin.TabularInline):
    model = ScheduledMatch
    fields = ['match', 'round', 'table', 'start_time', 'end_time']
    extra = 1

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    fields = ['id', 'active', 'desc']
    readonly_fields = ['id', 'active']
    list_display = ['id', 'desc', 'active']
    list_editable = ['desc']
    list_filter = ['active']
    inlines = [
        ScheduledMatchInline
    ]

    actions = ['mark_as_active', 'mark_as_not_active']

    def mark_as_active(self, request, queryset):
        try:
            to_activate = queryset.get()
        except MultipleObjectsReturned:
            self.message_user(
                request,
                _('Only one schedule can be active at a time'),
                messages.ERROR
            )
            return
        try:
            current_active = Schedule.objects.get(active=True)
        except Schedule.DoesNotExist:
            current_active = None
        with transaction.atomic():
            if current_active is not None:
                current_active.active = False
                current_active.save()
            to_activate.active = True
            to_activate.save()
        self.message_user(
            request,
            _('%s is now the active schedule.') % (to_activate,),
            messages.SUCCESS
        )
        if current_active is not None:
            self.message_user(
                request,
                _('%s is no longer the active schedule.') % (current_active,),
                messages.INFO
            )
    mark_as_active.short_description = gettext_lazy("Mark as active")

    def mark_as_not_active(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(
            request,
            ngettext(
                '%d schedule marked as not active.',
                '%d schedules marked as not active.',
                updated
            ) % (updated,),
            messages.SUCCESS
        )
    mark_as_not_active.short_description = gettext_lazy("Mark as not active")

    def response_change(self, request, obj):
        if "x-mark-active" in request.POST:
            if not obj.active:
                try:
                    current_active = Schedule.objects.get(active=True)
                except Schedule.DoesNotExist:
                    current_active = None
                with transaction.atomic():
                    if current_active is not None:
                        current_active.active = False
                        current_active.save()
                    obj.active = True
                    obj.save()
                self.message_user(
                    request,
                    _('%s is now the active schedule.')
                    % (obj),
                    messages.SUCCESS
                )
                if current_active is not None:
                    self.message_user(
                        request,
                        _('%s is no longer the active schedule.') % (current_active,),
                        messages.INFO
                    )

            # Return the same page, as done by Django on save.
            # See: django.contrib.admin.options:changelist_view
            return HttpResponseRedirect(request.get_full_path())
        elif "x-mark-not-active" in request.POST:
            if obj.active:
                obj.active = False
                obj.save()
                self.message_user(
                    request,
                    _('%s is no longer active.') % (obj,),
                    messages.SUCCESS
                )
            # Return the same page
            return HttpResponseRedirect(request.get_full_path())
        return super().response_change(request, obj)
