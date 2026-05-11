"""The thermostat. Not stealing, but allowed.

baseline:  5% always available to the loom
idle:      up to 15% when system load has been low for 60+ seconds
active:    snap back to baseline the moment the workshop heats up
"""
import time
import psutil


BASELINE_CEILING = 5
IDLE_CEILING = 15
IDLE_THRESHOLD_PCT = 20
IDLE_GRACE_SECONDS = 60


class Governor:
    def __init__(self):
        self._idle_since = None
        self.ceiling = BASELINE_CEILING

    def update(self):
        sys_cpu = psutil.cpu_percent(interval=None)
        now = time.time()
        if sys_cpu < IDLE_THRESHOLD_PCT:
            if self._idle_since is None:
                self._idle_since = now
            elif now - self._idle_since >= IDLE_GRACE_SECONDS:
                self.ceiling = IDLE_CEILING
        else:
            self._idle_since = None
            self.ceiling = BASELINE_CEILING
        return self.ceiling

    def sleep_for_duty_cycle(self, work_seconds):
        """After doing `work_seconds` of work, sleep so the duty cycle honors the ceiling.

        Duty cycle = ceiling%. If work took T seconds, sleep T * (100-ceiling)/ceiling.
        Clamped between 0.2s and 5s so the loop stays alive.
        """
        if self.ceiling >= 100:
            return
        sleep_for = work_seconds * (100 - self.ceiling) / max(self.ceiling, 1)
        sleep_for = max(0.2, min(5.0, sleep_for))
        time.sleep(sleep_for)
