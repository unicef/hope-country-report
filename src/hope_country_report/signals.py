import django.dispatch

report_completed = django.dispatch.Signal()
report_failed = django.dispatch.Signal()
