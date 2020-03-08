from django.contrib import admin
from .models import Score, PartialScore, Match, MatchResult
from django.utils.translation import gettext_lazy as _, pgettext

# Register your models here.
# admin.site.register(Score)
# admin.site.register(Match)
class ScoreInline(admin.StackedInline):
    model = Score
    fieldsets = [
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
    # Translators: This is shown on the admin interface when a score has not
    # been calculated (e.g. because the match hasn't been scored yet)
    NO_SCORE_AVAILABLE = pgettext('no score available', 'N/A')

    readonly_fields = ('white_score', 'black_score',
        'white_qualification_points', 'black_qualification_points', 'result')

    fieldsets = [
        (None, {
            'fields': ['status', ('white_team', 'black_team')]
        }),
        (_('Calculated score'), {
            'fields': [('white_score', 'black_score'),
                ('white_qualification_points', 'black_qualification_points'),
                'result'],
            'description': _('Calculated score for this match. This score is '
                'based on the <strong>final</strong> score, not on partial ones. '
                'To change these values, alter the corresponding fields on the '
                'score table.')
        })
    ]
    inlines = [
        WhitePartialScoreInline,
        BlackPartialScoreInline,
        ScoreInline
    ]

    def white_score(self, obj):
        score = obj.white_score
        return score if score is not None else self.NO_SCORE_AVAILABLE

    def black_score(self, obj):
        score = obj.black_score
        return score if score is not None else self.NO_SCORE_AVAILABLE

    def white_qualification_points(self, obj):
        points = obj.white_qualification_points
        return points if points is not None else self.NO_SCORE_AVAILABLE

    def black_qualification_points(self, obj):
        points = obj.black_qualification_points
        return points if points is not None else self.NO_SCORE_AVAILABLE

    def result(self, obj):
        result = obj.result
        return MatchResult(result).description if result is not None else self.NO_SCORE_AVAILABLE

    def get_queryset(self, request):
        return self.model.scored_objects.get_queryset()
