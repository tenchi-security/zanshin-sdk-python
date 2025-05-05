import json
from typing import Optional
from pydantic import BaseModel, Field

from zanshinsdk.common.enums import Frequency, TimeOfDay, Day


class ScanTargetSchedule(BaseModel):
    frequency: Frequency
    time_of_day: Optional[TimeOfDay] = Field(TimeOfDay.NIGHT, alias="timeOfDay")
    day: Optional[Day] = Day.SUNDAY

    def value(self):
        if self.frequency in (Frequency.SIX_HOURS, Frequency.TWELVE_HOURS):
            return {"frequency": self.frequency.value}
        if self.frequency == Frequency.WEEKLY:
            return {
                "frequency": self.frequency.value,
                "timeOfDay": self.time_of_day.value,
                "day": self.day.value,
            }
        return {
            "frequency": self.frequency.value,
            "timeOfDay": self.time_of_day.value,
        }

    def json(self):
        return json.dumps(self.value())


DAILY = ScanTargetSchedule(frequency=Frequency.DAILY, time_of_day=TimeOfDay.NIGHT)
WEEKLY = ScanTargetSchedule(
    frequency=Frequency.WEEKLY, time_of_day=TimeOfDay.NIGHT, day=Day.SUNDAY
)
