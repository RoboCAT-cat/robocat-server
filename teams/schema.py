import graphene
from graphene_django import DjangoObjectType
from .models import Category, Team, Institution

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ['name', 'colour']

    id = graphene.NonNull(graphene.ID)

    def resolve_id(self, info, **kwargs):
        return self.key

class TeamType(DjangoObjectType):
    class Meta:
        model = Team
        fields = ['name', 'category']
        # raffle is intentionally ommited: it should be considered an implementation detail

    id = graphene.NonNull(graphene.ID)
    institution_name = graphene.NonNull(graphene.String)

    def resolve_id(self, info, **kwargs):
        return self.key

    def resolve_institution_name(self, info, **kwargs):
        return self.institution.name

class RankedTeamType(TeamType):
    class Meta:
        model = Team
        fields = ['name', 'category']

    qualification_points = graphene.Int()
    total_score = graphene.Int()

    def resolve_qualification_points(self, info, **kwargs):
        return self.qualification_points

    def resolve_total_score(self, info, **kwargs):
        return self.total_score

class Query:
    all_categories = graphene.List(graphene.NonNull(CategoryType))
    category = graphene.Field(CategoryType, categoryId=graphene.String(required=True))

    all_teams = graphene.List(graphene.NonNull(TeamType))
    team = graphene.Field(TeamType, teamId=graphene.String(required=True))

    ranking = graphene.List(RankedTeamType)
    ranked_team = graphene.Field(RankedTeamType, teamId=graphene.String(required=True))

    def resolve_all_categories(self, info, **kwargs):
        return Category.objects.all()

    def resolve_category(self, info, categoryId, **kwargs):
        return Category.objects.filter(key=categoryId).first()

    def resolve_all_teams(self, info, **kwargs):
        return Team.objects.all()

    def resolve_team(self, info, teamId, **kwargs):
        return Team.objects.filter(key=teamId).first()

    def resolve_ranking(self, info, **kwargs):
        return Team.ranked_objects.order_by('-qualification_points', '-total_score', 'raffle')

    def ranked_team(self, info, teamId, **kwargs):
        return Team.ranked_objects.filter(key=teamId).first()
