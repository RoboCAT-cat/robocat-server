from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Q, Case, When, ExpressionWrapper

# Create your models here.
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
    black_disqualified = models.BooleanField(verbose_name=_('black is disqualified'))
    white_disqualified = models.BooleanField(verbose_name=_('white is disqualified'))

    # Stall: If a robot is stuck for more than 10 seconds, it can be moved
    # to its initial position. If the team does so, the robot has "stalled",
    # and a penalty of 10 points is received. This can only be done once per match.
    # Effects: if self.stalled: self.score -= 10
    black_stalled = models.BooleanField(verbose_name=_('black has stalled'))
    white_stalled = models.BooleanField(verbose_name=_('white has stalled'))

    # Cubes on lower goal: Cubes on this team's lower goal
    # Effects: other.score += self.cubes_on_lower
    cubes_on_lower_black = models.PositiveIntegerField(verbose_name=_("cubes on black's lower goal"))
    cubes_on_lower_white = models.PositiveIntegerField(verbose_name=_("cubes on white's lower goal"))

    # Cubes on upper goal: Cubes on this team's upper goal
    # Effects: other.score += 5 * self.cubes_on_upper
    cubes_on_upper_black = models.PositiveIntegerField(verbose_name=_("cubes on black's upper goal"))
    cubes_on_upper_white = models.PositiveIntegerField(verbose_name=_("cubes on white's upper goal"))

    # Cubes on field: Cube on this team's field
    # Effects: if self.cubes_on_field < other.cubes_on_field: self.score += 10
    cubes_on_black_field = models.PositiveIntegerField(verbose_name=_('cubes on black field'))
    cubes_on_white_field = models.PositiveIntegerField(verbose_name=_('cubes on white field'))

    @staticmethod
    def white_score_q():
        """
        Generate a Django Expression that can be used with .annotate()
        to obtain the score of the white team.
        """
        score = ExpressionWrapper(
            F('cubes_on_lower_black')
            + 5 * F('cubes_on_upper_black')
            + Case(
                When(cubes_on_white_field__lt=F('cubes_on_black_field'), then=10),
                default=0
            )
            + Case(
                When(white_stalled=True, then=-10),
                default=0
            ),
            output_field=models.IntegerField()
        )
        return Case(
            When(white_disqualified=True, then=0),
            default=score
        )

    @property
    def white_score(self):
        if self.white_disqualified:
            return 0
        score = 0
        if self.white_stalled:
            score -= 10
        score += self.cubes_on_lower_black
        score += 5 * self.cubes_on_upper_black
        if self.cubes_on_white_field < self.cubes_on_black_field:
            score += 10
        return score

    @staticmethod
    def black_score_q():
        """
        Generate a Django Expression that can be used with .annotate()
        to obtain the score of the black team.
        """
        score = ExpressionWrapper(
            F('cubes_on_lower_white')
            + 5 * F('cubes_on_upper_white')
            + Case(
                When(cubes_on_black_field__lt=F('cubes_on_white_field'), then=10),
                default=0
            )
            + Case(
                When(black_stalled=True, then=-10),
                default=0
            ),
            output_field=models.IntegerField()
        )
        return Case(
            When(black_disqualified=True, then=0),
            default=score
        )

    @property
    def black_score(self):
        if self.black_disqualified:
            return 0
        score = 0
        if self.black_stalled:
            score -= 10
        score += self.cubes_on_lower_white
        score += 5 * self.cubes_on_upper_white
        if self.cubes_on_black_field < self.cubes_on_white_field:
            score += 10
        return score

    @property
    def white_won(self):
        return (not self.white_disqualified) and (self.black_disqualified
            or self.white_score > self.black_score)

    @property
    def black_won(self):
        return (not self.black_disqualified) and (self.white_disqualified
            or self.black_score > self.white_score)

    @property
    def white_qualification_points(self):
        if self.white_disqualified:
            return 0
        elif self.white_won:
            return 3
        elif self.black_won:
            return 0
        else:
            return 1

    @property
    def black_qualification_points(self):
        if self.black_disqualified:
            return 0
        elif self.black_won:
            return 3
        elif self.white_won:
            return 0
        else:
            return 1
