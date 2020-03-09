import graphene
from graphene_django import DjangoObjectType
from .models import Match, MatchResult, Score

class ScoreType(DjangoObjectType):
    class Meta:
        model = Score
        fields = ['white_disqualified', 'black_disqualified', 'white_stalled',
            'black_stalled', 'cubes_on_lower_white', 'cubes_on_lower_black',
            'cubes_on_upper_white', 'cubes_on_upper_black',
            'cubes_on_white_field', 'cubes_on_black_field',
            'white_adhoc', 'black_adhoc', 'notes']

class MatchType(DjangoObjectType):
    class Meta:
        model = Match
        fields = ['id', 'white_team', 'black_team', 'status', 'score']

MatchResultEnum = graphene.Enum.from_enum(MatchResult, description=lambda v:
    v.description if v is not None else None)

class ScoredMatchType(DjangoObjectType):
    class Meta:
        model = Match
        fields = ['id', 'white_team', 'black_team', 'status', 'score']

    white_score = graphene.Int()
    black_score = graphene.Int()
    white_qualification_points = graphene.Int()
    black_qualification_points = graphene.Int()
    result = MatchResultEnum()

    def resolve_white_score(self, info, **kwargs):
        return self.white_score

    def resolve_black_score(self, info, **kwargs):
        return self.black_score

    def resolve_white_qualification_points(self, info, **kwargs):
        return self.white_qualification_points

    def resolve_black_qualification_points(self, info, **kwargs):
        return self.black_qualification_points

    def resolve_result(self, info, **kwargs):
        return self.result

class Query:
    all_matches = graphene.List(graphene.NonNull(MatchType))
    match = graphene.Field(MatchType, matchId=graphene.UUID(required=True))
    all_scored_matches = graphene.List(graphene.NonNull(ScoredMatchType))
    scored_match = graphene.Field(ScoredMatchType, matchId=graphene.UUID(required=True))

    def resolve_all_matches(self, info, **kwargs):
        return Match.objects.all()

    def resolve_match(self, info, matchId, **kwargs):
        return Match.objects.filter(id=matchId).first()

    def resolve_all_scored_matches(self, info, **kwargs):
        return Match.scored_objects.all()

    def resolve_scored_match(self, info, matchId, **kwargs):
        return Match.scored_objects.filter(id=matchId).first()
