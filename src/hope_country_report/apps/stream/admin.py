from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "office", "query", "enabled", "publish_as_url")
    search_fields = ("name",)
    list_filter = ("office", "query", "enabled", "publish_as_url")
