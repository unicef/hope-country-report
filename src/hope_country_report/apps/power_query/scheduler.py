from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler, debug, ModelEntry


class PQScheduler(DatabaseScheduler):
    Model = PeriodicTask
    Entry = ModelEntry

    def all_as_schedule(self):
        debug("DatabaseScheduler: Fetching database schedule")
        s = {}
        for model in self.Model.objects.enabled():
            try:
                s[model.name] = self.Entry(model, app=self.app)
            except ValueError:
                pass
        return s
