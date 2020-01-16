from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Category(models.Model):
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    key = models.SlugField(unique=True, verbose_name=_('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
    colour = models.CharField(max_length=20, verbose_name=_('colour'),
        help_text=_("HTML colour used to visually identify this category"))

class Institution(models.Model):
    class Meta:
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')

    key = models.SlugField(unique=True, verbose_name=_('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
    contact_info = models.TextField(blank=True, verbose_name=_('contact information'))

class Team(models.Model):
    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    key = models.SlugField(unique=True, verbose_name=('key ID'))
    name = models.CharField(max_length=80, verbose_name=_('name'))
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
