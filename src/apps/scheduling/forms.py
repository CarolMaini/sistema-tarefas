from django import forms
from django.contrib.auth import get_user_model

from apps.tasks.models import TaskExecution

from .models import ScheduleRule

DATETIME_FIELD_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-800 focus:border-slate-600 focus:outline-none"
)
TEXTAREA_CLASSES = DATETIME_FIELD_CLASSES
FILE_FIELD_CLASSES = (
    "block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 "
    "file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-semibold "
    "file:text-slate-800"
)


class TaskExecutionForm(forms.ModelForm):
    class Meta:
        model = TaskExecution
        fields = ["started_at", "ended_at", "comments", "attachment"]
        labels = {
            "started_at": "Horário de início",
            "ended_at": "Horário de fim",
            "comments": "Comentários da execução",
            "attachment": "Imagem ou PDF de evidência",
        }
        widgets = {
            "started_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": DATETIME_FIELD_CLASSES,
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "ended_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": DATETIME_FIELD_CLASSES,
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "comments": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": TEXTAREA_CLASSES,
                },
            ),
            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": FILE_FIELD_CLASSES,
                    "accept": ".jpg,.jpeg,.png,.pdf",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["started_at"].required = True
        self.fields["ended_at"].required = True


class ScheduleRuleForm(forms.ModelForm):
    weekdays = forms.MultipleChoiceField(
        choices=[
            (1, "Segunda-feira"),
            (2, "Terça-feira"),
            (3, "Quarta-feira"),
            (4, "Quinta-feira"),
            (5, "Sexta-feira"),
            (6, "Sábado"),
            (7, "Domingo"),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Dias da semana",
    )

    assignee = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label="Responsável padrão",
    )

    class Meta:
        model = ScheduleRule
        fields = [
            "frequency",
            "starts_on",
            "ends_on",
            "weekdays",
            "anchor_date",
            "assignee",
        ]
        widgets = {
            "starts_on": forms.DateInput(attrs={"type": "date"}),
            "ends_on": forms.DateInput(attrs={"type": "date"}),
            "anchor_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        workspace = kwargs.pop("workspace", None)
        super().__init__(*args, **kwargs)

        if workspace:
            users = [workspace.owner]
            users.extend(
                membership.user
                for membership in workspace.memberships.select_related("user").filter(
                    is_active=True,
                )
            )
            user_ids = {user.pk for user in users if user is not None}
            self.fields["assignee"].queryset = (
                get_user_model()
                .objects.filter(pk__in=user_ids)
                .order_by("username")
            )

        if self.instance and self.instance.pk:
            self.fields["weekdays"].initial = [
                str(day) for day in (self.instance.weekdays or [])
            ]

    def clean_weekdays(self):
        values = self.cleaned_data.get("weekdays", [])
        return [int(value) for value in values]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.weekdays = self.cleaned_data.get("weekdays", [])
        if commit:
            instance.save()
        return instance
