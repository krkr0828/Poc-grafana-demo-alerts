"""疑似設備アラート受信 Lambda."""

import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ["TABLE_NAME"]
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

REQUIRED_FIELDS = [
    "alertId",
    "facilityId",
    "facilityName",
    "severity",
    "alertType",
    "message",
    "occurredAt",
]
VALID_SEVERITIES = {"critical", "warning", "info"}

_dynamodb = boto3.resource("dynamodb")
_table = _dynamodb.Table(TABLE_NAME)


def _log(level, event, alert_id=None, message="", **extra):
    entry = {"level": level, "event": event, "alertId": alert_id, "message": message}
    entry.update(extra)
    print(json.dumps(entry, ensure_ascii=False))


def _make_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def lambda_handler(event, context):
    alert_id = None
    try:
        body_raw = event.get("body")
        if not body_raw:
            _log("WARN", "VALIDATION_ERROR", message="Request body is empty")
            return _make_response(400, {"error": "EMPTY_BODY", "message": "Request body is required"})

        try:
            data = json.loads(body_raw)
        except json.JSONDecodeError:
            _log("WARN", "VALIDATION_ERROR", message="Invalid JSON")
            return _make_response(400, {"error": "INVALID_JSON", "message": "Request body must be valid JSON"})

        if not isinstance(data, dict):
            _log("WARN", "VALIDATION_ERROR", message="Body is not a JSON object")
            return _make_response(400, {"error": "INVALID_JSON", "message": "Request body must be a JSON object"})

        alert_id = data.get("alertId")
        _log("INFO", "REQUEST_RECEIVED", alert_id=alert_id, message="Request received",
             severity=data.get("severity"))

        for field in REQUIRED_FIELDS:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                _log("WARN", "VALIDATION_ERROR", alert_id=alert_id, field=field,
                     message=f"Required field '{field}' is missing or empty")
                return _make_response(400, {
                    "error": "MISSING_FIELD",
                    "message": f"Required field '{field}' is missing or empty",
                })

        if data["severity"] not in VALID_SEVERITIES:
            _log("WARN", "VALIDATION_ERROR", alert_id=alert_id, field="severity",
                 value=data["severity"],
                 message="severity must be one of: critical, warning, info")
            return _make_response(400, {
                "error": "INVALID_SEVERITY",
                "message": "severity must be one of: critical, warning, info",
            })

        try:
            datetime.fromisoformat(data["occurredAt"])
        except (ValueError, TypeError):
            _log("WARN", "VALIDATION_ERROR", alert_id=alert_id, field="occurredAt",
                 value=data["occurredAt"],
                 message="occurredAt must be ISO 8601 format")
            return _make_response(400, {
                "error": "INVALID_DATE_FORMAT",
                "message": "occurredAt must be ISO 8601 format (e.g., 2026-04-25T10:00:00+09:00)",
            })

        _log("INFO", "VALIDATION_OK", alert_id=alert_id, message="Validation passed")

        try:
            existing = _table.get_item(Key={"alertId": alert_id}).get("Item")
            if existing:
                _log("WARN", "DUPLICATE_ALERT_ID", alert_id=alert_id,
                     message="Existing alertId will be overwritten")
        except ClientError as e:
            _log("WARN", "DUPLICATE_CHECK_FAILED", alert_id=alert_id,
                 error_code=e.response["Error"]["Code"],
                 message="Could not check existing record; proceeding with put_item")

        data["receivedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        data["source"] = "api"
        data["status"] = "open"

        try:
            _table.put_item(Item=data)
        except ClientError as e:
            _log("ERROR", "STORE_ERROR", alert_id=alert_id,
                 error_code=e.response["Error"]["Code"],
                 message="Failed to store alert in DynamoDB")
            return _make_response(500, {
                "error": "STORE_ERROR",
                "message": "Failed to store alert. Please try again.",
            })

        _log("INFO", "STORED", alert_id=alert_id, message="Alert stored successfully")
        return _make_response(200, {
            "message": "alert accepted",
            "alertId": alert_id,
            "stored": True,
        })

    except Exception as e:
        _log("ERROR", "UNEXPECTED_ERROR", alert_id=alert_id,
             error_type=type(e).__name__, message=str(e))
        return _make_response(500, {
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred.",
        })
