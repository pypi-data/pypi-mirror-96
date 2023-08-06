from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_lab_admin
from ..forms import BoxTypeForm
from ..models import BoxType
from .base_model_admin import BaseModelAdmin


@admin.register(BoxType, site=edc_lab_admin)
class BoxTypeAdmin(BaseModelAdmin, admin.ModelAdmin):

    form = BoxTypeForm

    fieldsets = (
        (None, {"fields": ("name", "across", "down", "total", "fill_order")}),
        audit_fieldset_tuple,
    )

    list_display = ("name", "across", "down", "total")
