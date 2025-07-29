import logging
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)

app = Flask(__name__)
logging.info("Flask app criado.")

# Custom SpanExporter para logging
class LoggingSpanExporter(SpanExporter):
    def export(self, spans):
        logging.info(f"[LoggingSpanExporter] Exportando {len(spans)} span(s):")
        for span in spans:
            logging.info(f"[LoggingSpanExporter] Span: {span.name}, TraceId: {span.context.trace_id}, Status: {span.status.status_code}")
        return SpanExportResult.SUCCESS

    def shutdown(self):
        logging.info("[LoggingSpanExporter] Shutdown called")

# Setup tracing
resource = Resource.create({"service.name": "TraceChecklyPoC"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# OTLP Exporter (Checkly)
otlp_exporter = OTLPSpanExporter(
    endpoint="https://otel.eu-west-1.checklyhq.com/v1/traces",
    headers=(("authorization", "Bearer ot_461f7f9bcfed4e809597df214c522db4"),),
)
logging.info("OTLPSpanExporter configurado.")

# Processador para exportar spans ao Checkly
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Processador só para log local (útil para debugging/ambiente de dev)
tracer_provider.add_span_processor(BatchSpanProcessor(LoggingSpanExporter()))
logging.info("BatchSpanProcessors adicionados.")

tracer = trace.get_tracer(__name__)
FlaskInstrumentor().instrument_app(app)
logging.info("Flask instrumentado.")

@app.route("/ping")
def ping():
    logging.info("Recebido request em /ping")
    logging.debug("Headers: %s", dict(request.headers))
    try:
        with tracer.start_as_current_span("ping-span") as span:
            span.set_attribute("custom.attribute", "valor-exemplo")
            logging.info("Span 'ping-span' criado. Aguardando exportação automática pelo BatchSpanProcessor.")
            return "pong", 200
    except Exception as e:
        logging.exception("Erro ao criar/exportar span em /ping: %s", e)
        return "erro interno", 500

if __name__ == "__main__":
    logging.info("Rodando app na porta 8000")
    app.run(host="0.0.0.0", port=8000)