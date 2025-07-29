import logging
import os
import random
import time
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import Status, StatusCode

# Detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)

app = Flask(__name__)
logging.info("Flask app created.")

# Custom SpanExporter for logging
class LoggingSpanExporter(SpanExporter):
    def export(self, spans):
        logging.info(f"[LoggingSpanExporter] Exporting {len(spans)} span(s):")
        for span in spans:
            logging.info(f"[LoggingSpanExporter] Span: {span.name}, TraceId: {span.context.trace_id}, Status: {span.status.status_code}")
        return SpanExportResult.SUCCESS

    def shutdown(self):
        logging.info("[LoggingSpanExporter] Shutdown called")

# Setup tracing
resource = Resource.create({"service.name": "TraceChecklyPoC"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# OTLP Exporter (Checkly) – token via environment variable
checkly_token = os.environ.get("CHECKLY_OTEL_TOKEN")
if not checkly_token:
    raise EnvironmentError("Environment variable CHECKLY_OTEL_TOKEN not set. Please set it before starting the application.")

otlp_exporter = OTLPSpanExporter(
    endpoint="https://otel.eu-west-1.checklyhq.com/v1/traces",
    headers=(("authorization", f"Bearer {checkly_token}"),),
)
logging.info("OTLPSpanExporter configured.")

# Processor to export spans to Checkly
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Processor for local logging (useful for debugging/dev environments)
tracer_provider.add_span_processor(BatchSpanProcessor(LoggingSpanExporter()))
logging.info("BatchSpanProcessors added.")

tracer = trace.get_tracer(__name__)
FlaskInstrumentor().instrument_app(app)
logging.info("Flask instrumented.")

@app.route("/ping")
def ping():
    logging.info("Received request at /ping")
    logging.debug("Headers: %s", dict(request.headers))
    try:
        with tracer.start_as_current_span("ping-span") as span:
            # Simulate random delay (50% chance)
            if random.random() < 0.5:
                time.sleep(2)  # 2 seconds delay
                span.set_attribute("simulated.delay", "2s")
            # Simulate random error (30% chance)
            if random.random() < 0.3:
                span.set_status(Status(StatusCode.ERROR, "Simulated error"))
                raise Exception("Simulated error for tracing")
            span.set_attribute("custom.attribute", "example-value")
            logging.info("Span 'ping-span' created. Waiting for automatic export by BatchSpanProcessor.")
            return "pong", 200
    except Exception as e:
        logging.exception("Error creating/exporting span at /ping: %s", e)
        return "internal error", 500

@app.route("/fail")
def fail():
    with tracer.start_as_current_span("fail-span") as span:
        span.set_status(Status(StatusCode.ERROR, "Intentional fail"))
        raise Exception("Intentional failure for trace simulation")

if __name__ == "__main__":
    logging.info("Running app on port 8000")
    app.run(host="0.0.0.0", port=8000)