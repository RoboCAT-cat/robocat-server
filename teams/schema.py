import graphene
from graphene_django import DjangoObjectType
from .models import Category, Team

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class TeamType(DjangoObjectType):
    class Meta:
        model = Team

class Query:
    all_categories = graphene.List(graphene.NonNull(CategoryType))
    category = graphene.Field(CategoryType, categoryId=graphene.String(required=True))

    all_teams = graphene.List(graphene.NonNull(TeamType))
    team = graphene.Field(TeamType, teamId=graphene.String(required=True))

    def resolve_all_categories(self, info, **kwargs):
        return Category.objects.all()

    def resolve_category(self, info, categoryId, **kwargs):
        return Category.objects.filter(key=categoryId).first()

    def resolve_all_teams(self, info, **kwargs):
        return Team.objects.all()

    def resolve_team(self, info, teamId, **kwargs):
        return Team.objects.filter(key=teamId).first()
