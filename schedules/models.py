from django.db import models
from matches.models import Match
from django.utils.translation import (gettext_lazy as _, pgettext_lazy as p_)
import uuid

# Create your models here.
class Schedule(models.Model):
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    # We use a UUID PK field as this will be the ID used by the API. The default, implicit
    # PK is an autoincremented integer, but this can needlessly leak information about current
    # and past DB state. While mostly harmless (as only admins should be able to get this ID
    # and it is unlikely to be useful for an attack), adding this field replaces it with a
    # long, random PK.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(max_length=80, verbose_name=_('short name'),
        help_text=_('A short name to help distinguish the schedule'))
    matches = models.ManyToManyField(Match, through='ScheduledMatch')


class ScheduledMatch(models.Model):
    class Meta:
        verbose_name = _('scheduled match')
        verbose_name_plural = _('scheduled matches')

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name=_('schedule'))
    # A NULL match is interpreted as a break
    match = models.ForeignKey(
        Match,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='scheduled',
        verbose_name=_('match')
    )
    round = models.PositiveIntegerField(default=None, null=True, blank=True, verbose_name=_('round'))
    table = models.PositiveIntegerField(default=1, verbose_name=p_('competition field', 'table'))
    start_time = models.DateTimeField(verbose_name=_('start time'))
    end_time = models.DateTimeField(verbose_name=_('end time'))
