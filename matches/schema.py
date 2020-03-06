import graphene
from graphene_django import DjangoObjectType
from .models import Match

class MatchType(DjangoObjectType):
    class Meta:
        model = Match
        fields = ['id', 'white_team', 'black_team', 'status']

class ScoredMatchType(DjangoObjectType):
    class Meta:
        model = Match
        fields = ['id', 'white_team', 'black_team']

    white_score = graphene.Int()
    black_score = graphene.Int()
    white_qualification_points = graphene.Int()
    black_qualification_points = graphene.Int()

    def resolve_white_score(self, info, **kwargs):
        return self.white_score

    def resolve_black_score(self, info, **kwargs):
        return self.black_score

    def resolve_white_qualification_points(self, info, **kwargs):
        return self.white_score

    def resolve_black_qualification_points(self, info, **kwargs):
        return self.black_score

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
