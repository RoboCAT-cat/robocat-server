import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext as e_
from django.db.models import F, Q, Case, When, ExpressionWrapper
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from teams.models import Team

class ScoredMatchManager(models.Manager):
    @staticmethod
    def gen_expr_for_white_score():
        score = (
            F('score__cubes_on_lower_black')
            + 5 * F('score__cubes_on_upper_black')
            + Case(
                When(score__cubes_on_white_field__lt=F('score__cubes_on_black_field'), then=10),
                default=0
            )
            + Case(
                When(score__white_stalled=False, then=10),
                default=0
            )
        )
        return Case(
            When(score__white_disqualified=True, then=0),
            default=score
        ) + F('score__white_adhoc')

    @staticmethod
    def gen_expr_for_black_score():
        score = (
            F('score__cubes_on_lower_white')
            + 5 * F('score__cubes_on_upper_white')
            + Case(
                When(score__cubes_on_black_field__lt=F('score__cubes_on_white_field'), then=10),
                default=0
            )
            + Case(
                When(score__black_stalled=True, then=0),
                default=10
            )
        )
        return Case(
            When(score__black_disqualified=True, then=0),
            default=score
        ) + F('score__black_adhoc')

    @staticmethod
    def gen_expr_for_white_qual_points():
        return Case(
            When(score__white_disqualified=True, then=0),
            When(white_score__gt=F('black_score'), then=3),
            When(white_score=F('black_score'), then=1),
            When(white_score__lt=F('black_score'), then=0),
            output_field=models.IntegerField()
        )

    @staticmethod
    def gen_expr_for_black_qual_points():
        return Case(
            When(score__black_disqualified=True, then=0),
            When(black_score__gt=F('white_score'), then=3),
            When(black_score=F('white_score'), then=1),
            When(black_score__lt=F('white_score'), then=0),
            output_field=models.IntegerField()
        )

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate(white_score=self.gen_expr_for_white_score())
            .annotate(black_score=self.gen_expr_for_black_score())
            .annotate(white_qualification_points=self.gen_expr_for_white_qual_points())
            .annotate(black_qualification_points=self.gen_expr_for_black_qual_points())
        )

# Create your models here.
class Match(models.Model):
    class Meta:
        verbose_name = _('match')
        verbose_name_plural = _('matches')

    # Managers
    objects = models.Manager()
    scored_objects = ScoredMatchManager()

    class Status(models.TextChoices):
        NOT_PLAYED = 'NP', _('Not played')
        PLAYING = 'PL', _('Playing')
        SCORING = 'SC', _('Scoring')
        FINISHED = 'FI', _('Finished')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))

    # Side-note: White team (and white score, ...) refers to the team playing on the
    # white side of the field; black team, to the team playing on the black side of the field.
    # While the actual side on which the team has played is irrelevant, the software will refer
    # internally to the "white team" or "black team", and the front-end may choose to do so too.
    # If "switching sides" is to be expected, presentation software must be carefully designed
    # to avoid such references, as they may be confusing.

    # One of the teams may be NULL (but not both). In this case, it is a "bye" ("pase" in Spanish),
    # i.e. the player wins automatically. This may be needed in case there is an odd number of teams

    white_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_white',
        verbose_name=_('white team')
    )

    black_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_black',
        verbose_name=_('black team')
    )

    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NOT_PLAYED, verbose_name=_('status'))

    # Partial scores: On partial scores, the other team's score is ignored, so it is possible
    # to send the score of the two teams separately.

    def clean(self):
        super().clean()
        errors = []
        if self.white_team is None and self.black_team is None:
            errors.append(ValidationError(_("At least one team must be non-null"), 'both-teams-null'))
        if self.white_team is not None and self.black_team is not None and self.white_team.pk == self.black_team.pk:
            errors.append(ValidationError(_("A team may not play against itself"), 'team-against-itself'))
        if self.status == self.Status.FINISHED:
            if self.score is None:
                errors.append(ValidationError(_("A finished match must have a score"), 'finished-no-score'))
            if self.partial_black is not None or self.partial_white is not None:
                errors.append(ValidationError(_("A finished match may not have a partial score"), 'partial-score-on-finished'))
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        if self.black_team is None:
            desc = e_('White: %s (bye)') % (self.white_team,)
        elif self.white_team is None:
            desc = e_('Black: %s (bye)') % (self.black_team,)
        else:
            desc = e_('%(white)s vs %(black)s') % { 'white': self.white_team, 'black': self.black_team }
        return f'{desc} ({self.Status(self.status).label})'

_ADHOC_SCORE_HELP = _("Points given by the referres on exceptional or unforseen circumstances")

class Score(models.Model):
    # Note: The comments explaining the scoreing are for quick reference and by no means official.
    # Always refer to RoboCAT's bases and regulations (henceforth "The Rules") found on the website.
    class Meta:
        verbose_name = _('score')
        verbose_name_plural = _('scores')

    # Pseudocode: Each field contains a pseudocode explaining its effects, on which the following
    # conventions are used:
    # `self` is the current team, `other` is the adversary;
    # `score` and `qualification_points` are the results, the score and the qualification_points respectively
    # Assuming the white team, `self.x` is the `x_white` (or `white_x`) field
    # and `òther.x` is the `x_black` (or `black_x`) field. The converse is true for the black team.

    match = models.OneToOneField(
        'Match',
        on_delete=models.CASCADE,
        related_name='score',
        verbose_name=_('match')
    )

    # Disqualification: The referees may disqualify a team under the following circumstances:
    # a) an act outlined in The Rules as being disqualifying is commited,
    # b) an act is commited that the organization deems disqualifying, on the basis that undermines
    #    the event's code of conduct (i.e. the team cheats or otherwise seriously 
    #    and purposefully interferes with the match),
    # c) a team fails to show up to a match -- possibly after several calls, or
    # d) a team fails to abide by any other ad lib rule. Such rules are created when an
    #    unexpected situation not covered by The Rules is observed and acted upon*.
    #    Such rules are repeatedly communicated by the staff.
    # A disqualified team:
    # - does not receive any score for the match
    # - does not receive any qualification points, regardless
    #   of the other team's score, and whether it has also been disqualified.
    # * Ad-libbed rules are rare, and used mostly to prevent blatant loophole abuse.
    #   As a rule of thumb, a team should use common sense and, if in doubt, ask
    #   the organization when designing a strategy.
    # Effects: if self.disqualified: self.score = 0, self.qualification_points = 0
    white_disqualified = models.BooleanField(default=False, verbose_name=_('white is disqualified'))
    black_disqualified = models.BooleanField(default=False, verbose_name=_('black is disqualified'))

    # Stall: If a robot is stuck for more than 10 seconds, it can be moved
    # to its initial position. If the team does so, the robot has "stalled",
    # and a penalty of 10 points is received. This can only be done once per match.
    # Effects: if not self.stalled: self.score += 10
    white_stalled = models.BooleanField(default=False, verbose_name=_('white has stalled'))
    black_stalled = models.BooleanField(default=False, verbose_name=_('black has stalled'))

    # Cubes on lower goal: Cubes on this team's lower goal
    # Effects: other.score += self.cubes_on_lower
    cubes_on_lower_white = models.PositiveIntegerField(verbose_name=_("cubes on white's lower goal"))
    cubes_on_lower_black = models.PositiveIntegerField(verbose_name=_("cubes on black's lower goal"))

    # Cubes on upper goal: Cubes on this team's upper goal
    # Effects: other.score += 5 * self.cubes_on_upper
    cubes_on_upper_white = models.PositiveIntegerField(verbose_name=_("cubes on white's upper goal"))
    cubes_on_upper_black = models.PositiveIntegerField(verbose_name=_("cubes on black's upper goal"))

    # Cubes on field: Cube on this team's field
    # Effects: if self.cubes_on_field < other.cubes_on_field: self.score += 10
    cubes_on_white_field = models.PositiveIntegerField(verbose_name=_('cubes on white field'))
    cubes_on_black_field = models.PositiveIntegerField(verbose_name=_('cubes on black field'))

    # Ad-hoc points: If the referees deem it necessary, extra points may be awarded to or substracted
    # from a team. These fields should be used sparingly, mostly to handle unforeseen events or
    # to work around bugs on the software, and should be accompanied by a note justifying this decision.
    white_adhoc = models.IntegerField(default=0, verbose_name=_('ad-hoc points for white team'),
        help_text=_ADHOC_SCORE_HELP)
    black_adhoc = models.IntegerField(default=0, verbose_name=_('ad-hoc points for black team'),
        help_text=_ADHOC_SCORE_HELP)

    notes = models.TextField(blank=True, default='', verbose_name=_('notes'))

    @staticmethod
    def white_score_q():
        """
        Generate a Django Expression that can be used with .annotate()
        to obtain the score of the white team.
        """
        score = (
            F('cubes_on_lower_black')
            + 5 * F('cubes_on_upper_black')
            + Case(
                When(cubes_on_white_field__lt=F('cubes_on_black_field'), then=10),
                default=0
            )
            + Case(
                When(white_stalled=True, then=-10),
                default=0
            )
        )
        return Case(
            When(white_disqualified=True, then=0),
            default=score
        ) + F('white_adhoc')

    # @property
    # def white_score(self):
    #     score = 0
    #     score += self.white_adhoc
    #     if self.white_disqualified:
    #         return score
    #     if not self.white_stalled:
    #         score += 10
    #     score += self.cubes_on_lower_black or 0
    #     score += 5 * (self.cubes_on_upper_black or 0)
    #     if (self.cubes_on_white_field or 0) < (self.cubes_on_black_field or 0):
    #         score += 10
    #     score += self.white_adhoc
    #     return score

    # @property
    # def black_score(self):
    #     score = 0
    #     score += self.black_adhoc
    #     if self.black_disqualified:
    #         return 0
    #     if not self.black_stalled:
    #         score += 10
    #     score += self.cubes_on_lower_white or 0
    #     score += 5 * (self.cubes_on_upper_white or 0)
    #     if (self.cubes_on_black_field or 0) < (self.cubes_on_white_field or 0):
    #         score += 10
    #     return score

    # @property
    # def white_won(self):
    #     return (not self.white_disqualified) and (self.black_disqualified
    #         or self.white_score > self.black_score)

    # @property
    # def black_won(self):
    #     return (not self.black_disqualified) and (self.white_disqualified
    #         or self.black_score > self.white_score)

    # @property
    # def white_qualification_points(self):
    #     if self.white_disqualified:
    #         return 0
    #     elif self.white_won:
    #         return 3
    #     elif self.black_won:
    #         return 0
    #     else:
    #         return 1

    # @property
    # def black_qualification_points(self):
    #     if self.black_disqualified:
    #         return 0
    #     elif self.black_won:
    #         return 3
    #     elif self.white_won:
    #         return 0
    #     else:
    #         return 1

    def __str__(self):
        return e_('White: %(white_score)s; Black: %(black_score)s') % {
            'white_score': self.white_score,
            'black_score': self.black_score
        }

class PartialScore(models.Model):
    class Meta:
        verbose_name = _('partial score')
        verbose_name_plural = _('partial scores')

    match_as_white = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='partial_white',
        verbose_name=_('match as white')
    )

    match_as_black = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='partial_black',
        verbose_name=_('match as black')
    )

    disqualified = models.BooleanField(default=False, verbose_name=_('is disqualified'))
    stalled = models.BooleanField(default=False, verbose_name=_('has stalled'))
    cubes_on_lower_goal = models.PositiveIntegerField(verbose_name=_('cubes on lower goal'))
    cubes_on_upper_goal = models.PositiveIntegerField(verbose_name=_('cubes on upper goal'))
    cubes_on_field = models.PositiveIntegerField(verbose_name=_('cubes on field'))
    adhoc = models.IntegerField(default=0, verbose_name=_('ad-hoc points'))
    notes = models.TextField(blank=True, default='', verbose_name=_('notes'))

    def clean(self):
        super().clean()
        if (self.match_as_black is None) == (self.match_as_white is None):
            raise ValidationError(_("Exactly one of (match as black, match as white) must be non-null"),
                'inconsistent-match-association')

    def __str__(self):
        if self.match_as_white is not None:
            if self.match_as_white.white_team is not None:
                return e_('Partial score for %(team)s on %(match)s') % {
                    'team': self.match_as_white.white_team,
                    'match': self.match_as_white
                }
            else:
                return e_('Partial score for white team on %(match)s') % {
                    'match': self.match_as_white
                }
        elif self.match_as_black is not None:
            if self.match_as_black.black_team is not None:
                return e_('Partial score for %(team)s on %(match)s') % {
                    'team': self.match_as_black.black_team,
                    'match': self.match_as_black
                }
            else:
                return e_('Partial score for black team on %(match)s') % {
                    'match': self.match_as_black
                }
        else:
            return e_('[Detached partial score]')
