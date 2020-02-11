import graphene
from graphene_django import DjangoObjectType
from .models import Category

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class Query:
    all_categories = graphene.List(CategoryType)
    #category = graphene.Field(CategoryType)

    def resolve_all_categories(self, info, **kwargs):
        return Category.objects.all()
