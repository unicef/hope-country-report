from functools import update_wrapper
from inspect import isclass
from typing import List, TypeVar, Union

from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.admin.options import csrf_protect_m
from django.contrib.auth import get_permission_codename
from django.core.checks import Error
from django.db.models import ForeignKey, Model
from django.forms.widgets import MediaDefiningClass
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import RedirectView

from adminactions.helpers import AdminActionPermMixin
from smart_admin.mixins import LinkedObjectsMixin
from smart_admin.modeladmin import SmartModelAdmin

from .config import conf
from .exceptions import InvalidTenantError, TenantAdminError
from .skeleton import Skeleton

model_admin_registry = {}

_M = TypeVar("_M", bound=Model)


class AutoRegisterMetaClass(MediaDefiningClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class: "BaseTenantModelAdmin" = super().__new__(mcs, class_name, bases, attrs)
        if new_class.model:
            model_admin_registry[new_class.model] = new_class
        return new_class


class TenantTabularInline(TabularInline):
    tenant_filter_field = None

    def get_tenant_filter(self, request):
        if not self.target_field:
            raise ValueError(f"Set 'target_field' on {self} or override `get_queryset()` to enable queryset filtering")
        return {self.tenant_filter_field: conf.strategy.get_selected_tenant(request).pk}


class TenantPermissinMixin(ModelAdmin):
    pass


class BaseTenantModelAdmin(
    SmartModelAdmin,
    AdminActionPermMixin,
    LinkedObjectsMixin,
    TenantPermissinMixin,
    metaclass=AutoRegisterMetaClass,
):
    model: _M = None
    skeleton: Union[ModelAdmin, Skeleton] = None
    tenant_filter_field: str = ""
    # change_list_template = "tenant_admin/change_list.html"
    # change_form_template = "tenant_admin/change_form.html"
    # linked_objects_template = "tenant_admin/linked_objects.html"
    # add_form_template = "tenant_admin/change_form.html"
    # delete_confirmation_template = "delete_confirmation"
    # delete_selected_confirmation_template = None
    # object_history_template = None
    # popup_response_template = None

    writeable_fields: List[str] = []
    exclude: List[str] = []
    linked_objects_hide_empty = True

    @property
    def change_list_template(self):
        return "tenant_admin/change_list.html"

    @property
    def change_form_template(self):
        return "tenant_admin/change_form.html"

    @property
    def linked_objects_template(self):
        return "tenant_admin/linked_objects.html"

    # def __init__(self, model, admin_site):
    #     super().__init__(model, admin_site)
    #     if self.skeleton:
    #         if not (
    #             (isclass(self.skeleton) and issubclass(self.skeleton, Skeleton)) or isinstance(self.skeleton, Skeleton)
    #         ):
    #             self.skeleton = Skeleton(self.skeleton)
    #         self.skeleton.initialise(self)

    def get_inlines(self, request, obj=None):
        flt = list(filter(lambda x: not issubclass(x, TenantTabularInline), self.inlines))
        if flt:
            raise ValueError(
                f"{self}.inlines contains one or more invalid class(es). " f" {flt} " f"Only use `TenantTabularInline`"
            )
        return self.inlines

    def get_writeable_fields(self, request, obj=None):
        return list(self.writeable_fields) + list(self.get_exclude(request, obj))

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []
        writeable = self.get_writeable_fields(request, obj)
        all_fields = list(
            set(
                [field.name for field in self.opts.local_fields]
                + [field.name for field in self.opts.local_many_to_many]
            )
        )
        return [f for f in all_fields if f not in writeable]

    def get_tenant_filter(self, request):
        if not self.tenant_filter_field:
            raise ValueError(
                f"Set 'tenant_filter_field' on {self} or override `get_queryset()` to enable queryset filtering"
            )
        if self.tenant_filter_field == "__none__":
            return {}
        active_tenant = conf.strategy.get_selected_tenant(request)
        if not active_tenant:
            raise InvalidTenantError
        return {self.tenant_filter_field: active_tenant.pk}

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs.filter(**self.get_tenant_filter(request))

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                try:
                    return self.admin_site.admin_view(view)(*args, **kwargs)
                except TenantAdminError:
                    return redirect(f"{self.admin_site.name}:select_tenant")

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        base_urls = [
            path("", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            path("add/", wrap(self.add_view), name="%s_%s_add" % info),
            path(
                "<path:object_id>/history/",
                wrap(self.history_view),
                name="%s_%s_history" % info,
            ),
            path(
                "<path:object_id>/delete/",
                wrap(self.delete_view),
                name="%s_%s_delete" % info,
            ),
            path(
                "<path:object_id>/change/",
                wrap(self.change_view),
                name="%s_%s_change" % info,
            ),
            # For backwards compatibility (was the change url before 1.9)
            path(
                "<path:object_id>/",
                wrap(RedirectView.as_view(pattern_name="%s:%s_%s_change" % ((self.admin_site.name,) + info))),
            ),
        ]
        return self.get_extra_urls() + base_urls

    def has_module_permission(self, request):
        return conf.auth.has_module_perms(request, self.opts.app_label)

    def get_all_permissions(self, request, obj=None):
        return conf.auth.get_all_permissions(request, obj)

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("change", opts)
        perm = "%s.%s" % (opts.app_label, codename)
        return perm in self.get_all_permissions(request, obj)

    def has_add_permission(self, request):
        opts = self.opts
        codename = get_permission_codename("add", opts)
        perm = "%s.%s" % (opts.app_label, codename)
        return perm in self.get_all_permissions(request)

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("view", opts)
        perm = "%s.%s" % (opts.app_label, codename)
        return perm in self.get_all_permissions(request, obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename("delete", opts)
        perm = "%s.%s" % (opts.app_label, codename)
        return perm in self.get_all_permissions(request, obj)


class TenantModelAdmin(BaseTenantModelAdmin):
    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if cls.model == conf.tenant_model:
            errors.append(Error(f'"{cls.__name__}.model cannot be {conf.tenant_model}" ', id="admin_tenant.E101"))
        return errors

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field == self.tenant_field:
            formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)
            return formfield
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_exclude(self, request, obj=None):
        if self.tenant_field:
            return [self.tenant_field.name]
        return []

    def save_form(self, request, form, change):
        if self.tenant_field.name != "__none__":
            setattr(
                form.instance,
                self.tenant_field.name,
                conf.strategy.get_selected_tenant(request),
            )
        return super().save_form(request, form, change)

    def get_adding_fields(self, request, obj=None):
        fields = self.model._meta.get_fields()
        required_fields = []
        for f in fields:
            if f.concrete and not getattr(f, "blank", False):
                required_fields.append(f.name)
        return required_fields

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            kwargs["fields"] = self.get_adding_fields(request, obj)
        return super().get_form(request, obj, change, **kwargs)

    @cached_property
    def tenant_field(self):
        if self.tenant_filter_field == "__none__":
            return None
        elif "." not in self.tenant_filter_field:
            return getattr(self.model, self.tenant_filter_field).field
        else:
            fields = self.model._meta.get_fields()
            for f in fields:
                if isinstance(f, ForeignKey):
                    if f.related_model == conf.tenant_model:
                        return f


class MainTenantModelAdmin(BaseTenantModelAdmin):
    model: _M = None

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if cls.model != conf.tenant_model:
            errors.append(
                Error(
                    f'"{cls.__name__}.model must be {conf.tenant_model}" ',
                    id="admin_tenant.E100",
                )
            )
        return errors

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        active_tenant = conf.strategy.get_selected_tenant(request)
        if not active_tenant:
            raise InvalidTenantError
        return qs.filter(pk=active_tenant.pk)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        object_id = str(conf.strategy.get_selected_tenant(request).pk)
        return super().change_view(request, object_id)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
