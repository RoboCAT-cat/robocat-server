import graphene
from graphene_django import DjangoObjectType
from .models import Match

class MatchType(DjangoObjectType):
    class Meta:
        model = Match
        fields = ['id', 'white_team', 'black_team', 'status']

class Query:
    all_matches = graphene.List(graphene.NonNull(MatchType))
    match = graphene.Field(MatchType, matchId=graphene.UUID(required=True))

    def resolve_all_matches(self, info, **kwargs):
        return Match.objects.all()

    def resolve_match(self, info, matchId, **kwargs):
        return Match.objects.filter(id=matchId).first()
