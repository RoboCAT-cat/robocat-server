from django.db import models
from django.db.models import Q, F
from django.utils.translation import (gettext_lazy as _, pgettext_lazy, gettext)
from matches.models import Match

class Schedule(models.Model):
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    active = models.BooleanField(default=False, verbose_name=_("active"))
    desc = models.CharField(
        max_length=80,
        blank=True,
        default='',
        verbose_name=_("description"),
        help_text=_("Short description to identify the schedule. Only informative")
    )

    def __str__(self):
        if self.desc:
            return gettext('Schedule %(id)d: %(desc)s') % {'id': self.id, 'desc': self.desc}
        else:
            return gettext('Schedule %d') % (self.id,)

class ScheduledMatch(models.Model):
    class Meta:
        verbose_name = _('scheduled match')
        verbose_name_plural = _('scheduled matches')
        constraints = [
            models.CheckConstraint(check=Q(end_time__gte=F('start_time')), name='coherent_time'),
            models.UniqueConstraint(fields=('schedule', 'match'), name='no_match_repetition')
        ]

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        verbose_name=_('schedule'),
        related_name='matches'
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=('match'),
        related_name='scheduled_on',
        help_text=_("Related match, or empty for 'to-be-decided'")
    )
    round = models.PositiveIntegerField(default=None, null=True, verbose_name=_('round'))
    table = models.PositiveIntegerField(default=1, verbose_name=pgettext_lazy('competition field', 'table'))
    start_time = models.DateTimeField(verbose_name=_('start time'))
    end_time = models.DateTimeField(verbose_name=_('end time'))
