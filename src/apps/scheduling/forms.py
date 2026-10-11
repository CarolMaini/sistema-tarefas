from django import forms
from django.contrib.auth import get_user_model

from .models import ScheduleRule


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
