from graphene import ObjectType, String, Schema, Field
from graphene_django.debug import DjangoDebug

from teams.schema import Query as TeamsQuery
from matches.schema import Query as MatchesQuery

class Query(ObjectType, TeamsQuery, MatchesQuery):
    debug = Field(DjangoDebug, name='_debug')

schema = Schema(query=Query)
