from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Sum
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, gettext
import random

# Create your models here.
class Category(models.Model):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    key = models.SlugField(unique=True, verbose_name=_('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
    colour = models.CharField(max_length=20, verbose_name=_('colour'),
        help_text=_("HTML colour used to visually identify this category"))

    def __str__(self):
        return self.name

class Institution(models.Model):
    class Meta:
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')

    key = models.SlugField(unique=True, verbose_name=_('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
    contact_info = models.TextField(blank=True, verbose_name=_('contact information'))

    def __str__(self):
        return self.name

class RankedTeamManager(models.Manager):
    @staticmethod
    def gen_qual_points_as_white():
        from matches.models import Match
        return Match.scored_objects.filter(white_team__id=OuterRef('id')).annotate(
            qp=Sum(Coalesce('white_qualification_points', 0))
        ).values('qp')

    @staticmethod
    def gen_qual_points_as_black():
        from matches.models import Match
        return Match.scored_objects.filter(black_team__id=OuterRef('id')).annotate(
            qp=Sum(Coalesce('black_qualification_points', 0))
        ).values('qp')

    @staticmethod
    def gen_score_as_white():
        from matches.models import Match
        return Match.scored_objects.filter(white_team__id=OuterRef('id')).annotate(
            s=Sum(Coalesce('white_score', 0))
        ).values('s')

    @staticmethod
    def gen_score_as_black():
        from matches.models import Match
        return Match.scored_objects.filter(white_team__id=OuterRef('id')).annotate(
            s=Sum(Coalesce('white_score', 0))
        ).values('s')

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate(_qpaw=self.gen_qual_points_as_white(),
                      _qpab=self.gen_qual_points_as_black(),
                      _saw=self.gen_score_as_white(),
                      _sab=self.gen_score_as_black())
            .annotate(qualification_points=Coalesce('_qpaw', 0) + Coalesce('_qpab', 0),
                total_score=Coalesce('_saw', 0) + Coalesce('_sab', 0))
        )

def gen_raffle_result():
    return random.randint(0, 2_147_483_647)

class Team(models.Model):
    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    # Managers:
    ranked_objects = RankedTeamManager()
    objects = models.Manager()

    key = models.SlugField(unique=True, verbose_name=('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
    raffle = models.PositiveIntegerField(
        default=gen_raffle_result,
        verbose_name=_('raffle result')
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name=_('institution')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='teams',
        verbose_name=_('category')
    )

    def reroll_raffle(self):
        self.raffle = gen_raffle_result()

    def __str__(self):
        return self.name

class TeamMembership(models.Model):
    class Meta:
        verbose_name = _('team membership')
        verbose_name_plural = _('team memberships')

        indexes = [
            models.Index(fields=('user',)),
            models.Index(fields=('team',))
        ]
        constraints = [
            models.UniqueConstraint(fields=('user', 'team'), name='no_redundant_membership')
        ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='team',
        verbose_name=_('user')
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('team')
    )

    def __str__(self):
        return gettext("%(user)s of team %(team)s") % { 'user': self.user, 'team': self.team }
