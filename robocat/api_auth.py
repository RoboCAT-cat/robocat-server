import graphene
from django.contrib.auth import authenticate, login, logout

class ApiLogin(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(parent, info, username, password):
        print(info.context.user)
        if info.context.user.is_authenticated:
            return {"ok": None}
        user = authenticate(info.context, username=username, password=password)
        if user is None:
            return {"ok": False}
        login(info.context, user)
        return {"ok": True}

class ApiLogout(graphene.Mutation):
    class Arguments:
        pass

    ok = graphene.Boolean(required=True)

    @staticmethod
    def mutate(parent, info):
        logout(info.context)
        return {"ok": True}

class Me(graphene.ObjectType):
    username = graphene.String(required=True)

    @staticmethod
    def resolve_username(parent, info, **kwargs):
        return parent.username

class Mutation:
    login = ApiLogin.Field()
    logout = ApiLogout.Field()

class Query:
    me = graphene.Field(Me)

    @staticmethod
    def resolve_me(parent, info, **kwargs):
        user = info.context.user
        if user.is_authenticated:
            return Me(user)
        else:
            return None
