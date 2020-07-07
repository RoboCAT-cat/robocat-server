import graphene
from graphene_django import DjangoObjectType
from .models import Schedule, ScheduledMatch

class ScheduledMatchType(DjangoObjectType):
    class Meta:
        model = ScheduledMatch
        fields = ['schedule', 'match', 'round', 'table', 'start_time', 'end_time']

class ScheduleType(DjangoObjectType):
    class Meta:
        model = Schedule
        fields = ['id', 'active', 'desc']

    id = graphene.ID()
    desc = graphene.String()
    matches = graphene.NonNull(graphene.List(graphene.NonNull(ScheduledMatchType)))

    def resolve_id(self, info, **kwargs):
        if info.context.user.is_staff:
            return self.id
        else:
            return None

    def resolve_desc(self, info, **kwargs):
        if info.context.user.is_staff:
            return self.desc
        else:
            return None

    def resolve_matches(self, info, **kwargs):
        return ScheduledMatch.objects.filter(schedule=self)

class Query:
    schedule = graphene.Field(ScheduleType, scheduleId=graphene.ID(required=False))
    all_schedules = graphene.List(graphene.NonNull(ScheduleType))

    def resolve_schedule(self, info, scheduleId=None, **kwargs):
        if scheduleId is None:
            return Schedule.objects.filter(active=True).first()
        elif not info.context.user.is_staff:
            return None
        else:
            return Schedule.objects.filter(id=scheduleId).first()

    def resolve_all_schedules(self, info, **kwargs):
        if info.context.user.is_staff:
            return Schedule.objects.all()
        else:
            return None
