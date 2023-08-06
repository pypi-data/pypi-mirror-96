from .address_model_admin_mixin import AddressModelAdminMixin
from .changelist_buttons import (
    ModelAdminChangelistButtonMixin,
    ModelAdminChangelistModelButtonMixin,
)
from .inlines import (
    LimitedAdminInlineMixin,
    StackedInlineModelAdminMixin,
    TabularInlineMixin,
)
from .model_admin_audit_fields_mixin import (
    ModelAdminAuditFieldsMixin,
    audit_fields,
    audit_fieldset_tuple,
)
from .model_admin_form_auto_number_mixin import ModelAdminFormAutoNumberMixin
from .model_admin_form_instructions_mixin import ModelAdminFormInstructionsMixin
from .model_admin_institution_mixin import ModelAdminInstitutionMixin
from .model_admin_model_redirect_mixin import ModelAdminModelRedirectMixin
from .model_admin_next_url_redirect_mixin import (
    ModelAdminNextUrlRedirectError,
    ModelAdminNextUrlRedirectMixin,
)
from .model_admin_redirect_on_delete_mixin import ModelAdminRedirectOnDeleteMixin
from .model_admin_replace_label_text_mixin import ModelAdminReplaceLabelTextMixin
from .model_admin_simple_history import SimpleHistoryAdmin
from .templates_model_admin_mixin import TemplatesModelAdminMixin
from .utils import get_next_url
