from django.db import models
from django.utils.translation import gettext_lazy as _
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

def gen_raffle_result():
    return random.randint(0, 2147483647)

class Team(models.Model):
    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

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
