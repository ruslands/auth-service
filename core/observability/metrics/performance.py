import psutil
import json
from pytz import HOUR
import redis
from datetime import datetime, timezone
from celery.utils.log import get_task_logger


from app.core.config import settings
from app.core.schemas.metrics import PerfMetrics

SEC = 1000
MIN = 60 * SEC
# HOUR = 60 * MIN
DAY = 24 * HOUR


class PerfMetricsLoader:
    r: redis.Redis
    start: int
    ts: any

    def __init__(self) -> None:
        self.logger = get_task_logger("PerfMetricsLoader")

    def init(self) -> None:
        self.r = redis.Redis.from_url(settings.REDIS_URI)
        self.start = self.utc_now()
        self.ts = self.r.ts()

        for metric in PerfMetrics.Keys:
            key = settings.PERF_METRICS_KEY_PREFIX + metric
            labels = {"metric": metric, "type": "performance"}
            duplicate_policy = "last"
            if not self.r.exists(key):
                self.ts.create(
                    key,
                    labels=labels,
                    duplicate_policy=duplicate_policy,
                    retention_msecs=HOUR,
                )
            if not self.r.exists(key + "_min"):
                self.ts.create(
                    key + "_min",
                    labels=labels,
                    duplicate_policy=duplicate_policy,
                    retention_msecs=DAY,
                )
            if not self.r.exists(key + "_hour"):
                self.ts.create(
                    key + "_hour", labels=labels, duplicate_policy=duplicate_policy
                )

            rules = self.ts.info(key).rules
            #  [[b'perf_data_cpu_p_min', 60000, b'AVG'], [b'perf_data_cpu_p_hour', 3600000, b'AVG']]
            if len(rules) < 1:
                self.ts.createrule(key, key + "_min", "avg", MIN)
            if len(rules) < 2:
                self.ts.createrule(key, key + "_hour", "avg", HOUR)

    def load(self) -> None:
        m = self._get_metrics()

        offset = m.ts - self.start

        for metric in PerfMetrics.Keys:
            key = settings.PERF_METRICS_KEY_PREFIX + metric
            self.ts.add(key, m.ts, getattr(m, metric))

        if offset % settings.PERF_METRICS_PUBLISH_STEP == 0:
            js = json.dumps(m, default=vars)
            self.r.publish(settings.PERF_METRICS_PS_CHANNEL, js)

    def utc_now(self) -> int:
        return int(datetime.now(timezone.utc).timestamp()) * 1000

    def _get_metrics(self) -> PerfMetrics:
        mem = psutil.virtual_memory()
        m = PerfMetrics(
            cpu_p=psutil.cpu_percent(),
            vm_p=mem.percent,
            ts=self.utc_now(),
        )

        return m
