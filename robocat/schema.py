from graphene import ObjectType, String, Schema, Field
from graphene_django.debug import DjangoDebug

from teams.schema import Query as TeamsQuery

class Query(ObjectType, TeamsQuery):
    debug = Field(DjangoDebug, name='_debug')

schema = Schema(query=Query)
