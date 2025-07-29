# TraceChecklyPoC Python

Proof of concept project for instrumenting Python APIs with OpenTelemetry and Checkly.

## Table of Contents
- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables Setup](#environment-variables-setup)
- [Running the API](#running-the-api)
- [OpenTelemetry Instrumentation](#opentelemetry-instrumentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [References](#references)

---

## About

This API demonstrates distributed tracing and monitoring in Python using OpenTelemetry and integration with Checkly.

## Prerequisites

- Python 3.8+
- pip
- Git

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/drigocsouza/tracechecklypoc-python.git
cd tracechecklypoc-python
pip install -r requirements.txt
```

## Environment Variables Setup

**Never expose sensitive tokens directly in your code!**

Create a `.env` file at the root of the project (do not commit this file) and add:
```
CHECKLY_OTEL_TOKEN=<your_checkly_token>
```
Or export it directly in your terminal (Linux/macOS):
```bash
export CHECKLY_OTEL_TOKEN=<your_checkly_token>
```
On Windows (CMD):
```cmd
set CHECKLY_OTEL_TOKEN=<your_checkly_token>
```

Add `.env` to `.gitignore` to ensure it is not versioned:
```
.env
```

## Running the API

With the environment variable set, run:
```bash
python app.py
```
The API will be available at `http://localhost:8000`.

## OpenTelemetry Instrumentation

- The code already includes tracer configuration and sends spans to Checkly via OTLP.
- To change to another backend, update the `endpoint` and `headers` in the OTLPSpanExporter section.

## Testing

It is recommended to use `pytest` for automated tests:

```bash
pytest
```

## Deployment

Use environments that allow secure configuration of environment variables (Docker, Heroku, cloud servers).

## References

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Checkly](https://www.checklyhq.com/)
- [Flask](https://flask.palletsprojects.com/)

---

**Questions or suggestions? Open an issue in this repository!**