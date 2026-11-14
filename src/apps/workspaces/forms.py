from django import forms
from django.contrib.auth import get_user_model

from .models import Workspace


class WorkspaceMemberChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        display_name = obj.display_name or obj.get_full_name() or obj.username
        return f"{display_name} ({obj.email})"


class WorkspaceMemberForm(forms.Form):
    member = WorkspaceMemberChoiceField(
        queryset=get_user_model()._default_manager.none(),
        label="Usuário disponível",
        empty_label="Selecione um usuário",
        error_messages={"invalid_choice": "Selecione um usuário disponível."},
        widget=forms.Select(
            attrs={
                "class": "member-add-select",
            }
        ),
    )

    def __init__(self, *args, workspace: Workspace, **kwargs):
        self.workspace = workspace
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        self.fields["member"].queryset = (
            user_model._default_manager.filter(is_active=True)
            .exclude(pk=workspace.owner_id)
            .exclude(workspace_memberships__workspace=workspace)
            .order_by("username")
        )
