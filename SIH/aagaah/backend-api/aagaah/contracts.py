from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator

class Status(StrEnum):
    LIVE = 'VERIFIED LIVE'
    MOCKED = 'MOCKED'
    REPLAY = 'REPLAY'
    PLANNED = 'PLANNED'

class Reading(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    location_id: str
    observed_at: AwareDatetime
    available_at: AwareDatetime
    source: str
    status: Status
    synthetic: bool = False
    rainfall_mm: float | None = Field(default=None, ge=0, le=500)
    soil_moisture: float | None = Field(default=None, ge=0, le=1)
    water_level_m: float | None = Field(default=None, ge=0, le=50)
    forecast_rain_mm: float | None = Field(default=None, ge=0, le=500)
    forecast_issued_at: AwareDatetime | None = None
    interval_minutes: int = Field(default=60, ge=1, le=1440)

    @model_validator(mode='after')
    def provenance(self):
        if self.synthetic and self.status == Status.LIVE:
            raise ValueError('Synthetic measurements cannot be VERIFIED LIVE')
        if self.available_at < self.observed_at:
            raise ValueError('Observation cannot become available before its valid time')
        if self.forecast_rain_mm is not None and self.forecast_issued_at is None:
            raise ValueError('Forecast requires an issue time')
        if self.status == Status.PLANNED:
            raise ValueError('A planned provider cannot produce observations')
        return self

class PredictRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    as_of: AwareDatetime
    readings: list[Reading] = Field(min_length=1, max_length=10000)

class ReplayControl(BaseModel):
    action: str = Field(pattern='^(play|pause|step|reset|seek)$')
    step: int | None = Field(default=None, ge=0, le=71)
