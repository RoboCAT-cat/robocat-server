from django.contrib import admin
from .models import Score, PartialScore, Match
from django.utils.translation import gettext_lazy as _

# Register your models here.
# admin.site.register(Score)
# admin.site.register(Match)
class ScoreInline(admin.StackedInline):
    model = Score
    readonly_fields = ['white_score', 'black_score',
        'white_qualification_points', 'black_qualification_points']
    fieldsets = [
        (None, {
            'fields': [('white_score', 'black_score'),
                ('white_qualification_points', 'black_qualification_points')]
        }),
        (_('Disqualifications'), {
            'fields': [('white_disqualified', 'black_disqualified')]
        }),
        (_('Stalls'), {
            'fields': [('white_stalled', 'black_stalled')]
        }),
        (_('Cubes on goals'), {
            'fields': [
                ('cubes_on_lower_white', 'cubes_on_upper_white'),
                ('cubes_on_lower_black', 'cubes_on_upper_black')
            ]
        }),
        (_('Cubes on fields'), {
            'fields': [
                'cubes_on_white_field', 'cubes_on_black_field'
            ]
        }),
        (_('Refereeing'), {
            'fields': ['white_adhoc', 'black_adhoc', 'notes'],
            'classes': ['collapse'],
            'description': _('Auxiliary fields used at the discretion of the referees')
        })
    ]

class PartialScoreInline(admin.StackedInline):
    model = PartialScore
    fields = [('disqualified', 'stalled'), ('cubes_on_lower_goal', 'cubes_on_upper_goal'), 'cubes_on_field', 'adhoc', 'notes']
    classes = ['collapse']

class WhitePartialScoreInline(PartialScoreInline):
    fk_name = 'match_as_white'
    verbose_name = _('white partial score')
    verbose_name_plural = _('white partial scores')

class BlackPartialScoreInline(PartialScoreInline):
    fk_name = 'match_as_black'
    verbose_name = _('black partial score')
    verbose_name_plural = _('black partial scores')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    fields = ('status', 'white_team', 'black_team')
    inlines = [
        WhitePartialScoreInline,
        BlackPartialScoreInline,
        ScoreInline
    ]
