# jetblack-metrics

Generic metric classes and context based monitoring.

## Installation

Install from the pie store.

```bash
pip install jetblack-metrics
```

## Usage

First you need to implement a metric which interacts with an actual
instrumentation implementation. The following provides an HTTP request
metric using Prometheus to gather the metrics and the `TimedMetric` to
provide a latency metric.

```python
from jetblack_metrics import monitor, TimedMetric
from prometheus_client import Counter, Gauge, Histogram

class HttpRequestMetric(TimedMetric):
    """
    A metric which holds HTTP information.
    """

    def __init__(self, name: str, method: str, path: str) -> None:
        super().__init__()
        self.name = name
        self.scope = method
        self.info = path
        self.status = 500

    REQUEST_COUNT = Counter(
        "http_request_count",
        "Number of requests received",
        ["name", "method", "path", "status"]
    )
    REQUEST_LATENCY = Histogram(
        "http_request_latency",
        "Elapsed time per request",
        ["name", "method", "path"]
    )
    REQUEST_IN_PROGRESS = Gauge(
        "http_requests_in_progress",
        "Requests in progress",
        ["name", "method", "path"]
    )

    def on_enter(self):
        super().on_enter()
        self.REQUEST_IN_PROGRESS.labels(
            self.name,
            self.scope['method'],
            self.scope['path']
        ).inc()

    def on_exit(self) -> None:
        super().on_exit()
        self.REQUEST_COUNT.labels(
            self.name,
            self.scope['method'],
            self.scope['path'],
            self.status
        ).inc()
        self.REQUEST_LATENCY.labels(
            self.name,
            self.scope['method'],
            self.scope['path']
        ).observe(self.elapsed)
        self.REQUEST_IN_PROGRESS.labels(
            self.name,
            self.scope['method'],
            self.scope['path']
        ).dec()
```

Once we have the metric we can use the `monitor` function to manage the process
of gathering the statistics.

```python
def some_http_middleware(request, next_handler):
    """Some kind of HTTP middleware function"""
    with monitor(HttpRequestMetric('MyApp', request.method, request.path)) as metric:
        # Call the request handler
        response = next_handler(request)
        metric.status = response.status
```
