from django.utils import timezone

import factory
from django_celery_beat.models import ClockedSchedule, IntervalSchedule, PeriodicTask, SOLAR_SCHEDULES, SolarSchedule
from factory.fuzzy import FuzzyChoice
from testutils.factories import AutoRegisterModelFactory


class IntervalScheduleFactory(AutoRegisterModelFactory):
    every = 1
    period = IntervalSchedule.HOURS

    class Meta:
        model = IntervalSchedule


class SolarScheduleFactory(AutoRegisterModelFactory):
    event = FuzzyChoice([x[0] for x in SOLAR_SCHEDULES])

    latitude = 10.1
    longitude = 10.1

    class Meta:
        model = SolarSchedule


class ClockedScheduleFactory(AutoRegisterModelFactory):
    clocked_time = timezone.now()

    class Meta:
        model = ClockedSchedule


class PeriodicTaskFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "PeriodicTask%03d" % n)
    interval = factory.SubFactory(IntervalScheduleFactory)
    task = "sos.tasks.notify_failures"

    class Meta:
        model = PeriodicTask
