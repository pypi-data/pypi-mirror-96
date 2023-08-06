from collections import namedtuple

from django import template
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from edc_appointment.constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from edc_appointment.models import Appointment
from edc_lab.models.manifest.consignee import Consignee

register = template.Library()


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/forms_button.html"
)
def forms_button(wrapper=None, visit=None):
    """wrapper is an AppointmentModelWrapper."""

    visit_pk = visit.id
    if visit_pk:
        btn_color = "btn-primary"
        title = ""
        fa_icon = "fas fa-list-alt"
        href = wrapper.forms_url
        label = _("Forms")
        label_fa_icon = "fas fa-share"
        visit_pk = str(visit_pk)
    else:
        btn_color = "btn-warning"
        title = _("Click to update the visit report")
        fa_icon = "fas fa-plus"
        href = visit.href
        label = _("Start")
        label_fa_icon = None
    btn_id = f"{label.lower()}_btn_{wrapper.visit_code}_{wrapper.visit_code_sequence}"
    return dict(
        btn_color=btn_color,
        btn_id=btn_id,
        fa_icon=fa_icon,
        href=href,
        label=label,
        label_fa_icon=label_fa_icon,
        title=title,
        visit_code=wrapper.visit_code,
        visit_code_sequence=wrapper.visit_code_sequence,
        visit_pk=visit_pk,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/" "appointment_in_progress.html"
)
def appointment_in_progress(subject_identifier=None, visit_schedule=None, schedule=None):

    try:
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            appt_status=IN_PROGRESS_APPT,
        )
    except ObjectDoesNotExist:
        visit_code = None
    except MultipleObjectsReturned:
        qs = Appointment.objects.filter(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            appt_status=IN_PROGRESS_APPT,
        )
        visit_code = ", ".join([obj.visit_code for obj in qs])
    else:
        visit_code = appointment.visit_code
    return dict(visit_code=visit_code)


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/"
    f"requisition_panel_actions.html",
    takes_context=True,
)
def requisition_panel_actions(context, requisitions=None):
    try:
        requisition_metadata = requisitions[0]
    except IndexError:
        context["verify_disabled"] = None
    else:
        app_label, model_name = requisition_metadata.model.split(".")
        context["verify_disabled"] = (
            None
            if context["user"].has_perm(f"{app_label}.change_{model_name}")
            else "disabled"
        )
    appointment = context.get("appointment")
    scanning = context.get("scanning")
    autofocus = "autofocus" if scanning else ""
    context["appointment"] = str(appointment.object.pk)
    context["autofocus"] = autofocus
    return context


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/"
    f"print_requisition_popover.html",
    takes_context=True,
)
def print_requisition_popover(context):
    C = namedtuple("Consignee", "pk name")
    consignees = []
    for consignee in Consignee.objects.all():
        consignees.append(C(str(consignee.pk), consignee.name))
    context["consignees"] = consignees
    return context


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/" f"appointment_status.html"
)
def appointment_status_icon(appt_status=None):
    return dict(
        appt_status=appt_status,
        NEW_APPT=NEW_APPT,
        IN_PROGRESS_APPT=IN_PROGRESS_APPT,
        INCOMPLETE_APPT=INCOMPLETE_APPT,
        COMPLETE_APPT=COMPLETE_APPT,
        CANCELLED_APPT=CANCELLED_APPT,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/dashboard/visit_button.html"
)
def show_dashboard_visit_button(wrapped_appointment=None):
    title = None
    label = None
    if wrapped_appointment.appt_status == NEW_APPT:
        label = _("Start visit")
        title = _("Start data collection for this timepoint.")
    elif wrapped_appointment.appt_status == IN_PROGRESS_APPT:
        label = _("Continue")
        title = _("Continue data collection for this timepoint.")
    elif wrapped_appointment.appt_status == INCOMPLETE_APPT:
        incomplete = _("Incomplete")
        label = mark_safe(
            f'<i class="fas fa-pencil-alt fa-sm" aria-hidden="true"></i> {incomplete}'
        )
        title = _("Continue data collection for this timepoint.")
    elif wrapped_appointment.appt_status == CANCELLED_APPT:
        label = _("Cancelled")
        title = _("Cancelled.")
    elif wrapped_appointment.appt_status == COMPLETE_APPT:
        pass
    return dict(wrapped_appointment=wrapped_appointment, title=title, label=label)
