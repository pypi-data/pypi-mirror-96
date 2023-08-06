# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
from typing import Dict

from opentelemetry.metrics import Meter

from azure_monitor.sdk.auto_collection.metrics_span_processor import (
    AzureMetricsSpanProcessor,
)
from azure_monitor.sdk.auto_collection.performance_metrics import (
    PerformanceMetrics,
)
from azure_monitor.sdk.auto_collection.request_metrics import RequestMetrics
from azure_monitor.sdk.auto_collection.utils import AutoCollectionType

__all__ = [
    "AutoCollection",
    "AutoCollectionType",
    "AzureMetricsSpanProcessor",
    "RequestMetrics",
    "PerformanceMetrics",
]


class AutoCollection:
    """Starts auto collection of performance counters

    Args:
        meter: OpenTelemetry Meter
        labels: Dictionary of labels
    """

    def __init__(self, meter: Meter, labels: Dict[str, str]):
        col_type = AutoCollectionType.PERF_COUNTER
        self._performance_metrics = PerformanceMetrics(meter, labels, col_type)
