from django.conf import settings

from .address_mixin import AddressMixin
from .base_model import BaseModel
from .base_uuid_model import BaseUuidModel
from .blood_pressure_model_mixin import BloodPressureModelMixin
from .fields import (
    DiastolicPressureField,
    DurationYMDField,
    HeightField,
    HostnameModificationField,
    IdentityTypeField,
    InitialsField,
    IsDateEstimatedField,
    IsDateEstimatedFieldNa,
    OtherCharField,
    SystolicPressureField,
    UserField,
    WaistCircumferenceField,
    WeightField,
)
from .fields.duration import DurationYearMonthField
from .historical_records import HistoricalRecords
from .report_status_model_mixin import ReportStatusModelMixin
from .url_model_mixin import UrlModelMixin, UrlModelMixinNoReverseMatch
from .utils import (
    InvalidFieldName,
    InvalidFormat,
    duration_to_date,
    estimated_date_from_ago,
)
from .validators import (
    bp_validator,
    cell_number,
    date_is_future,
    date_is_not_now,
    date_is_past,
    date_not_future,
    datetime_is_future,
    datetime_not_future,
    hm_validator,
    hm_validator2,
    telephone_number,
    ymd_validator,
)

if settings.APP_NAME == "edc_model":
    from ..tests.models import *  # noqa
