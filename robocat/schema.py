from graphene import ObjectType, String, Schema

from teams.schema import Query as TeamsQuery

class Query(ObjectType, TeamsQuery):
    pass

schema = Schema(query=Query)
