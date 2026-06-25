from datetime import datetime
from pathlib import Path


ALLOWED_UPLOAD_EXTENSIONS = {".xlsx"}
BLOCKED_UPLOAD_EXTENSIONS = {".xlsm", ".xls", ".xlsb", ".csv", ".exe", ".zip"}
MAX_UPLOAD_SIZE_MB = 10


class UploadSecurityError(ValueError):
    """Raised when an uploaded file fails security validation."""


def get_file_extension(filename):
    return Path(filename).suffix.lower()


def get_file_size_mb(uploaded_file):
    current_position = uploaded_file.tell()
    uploaded_file.seek(0, 2)
    size_bytes = uploaded_file.tell()
    uploaded_file.seek(current_position)
    return size_bytes / (1024 * 1024)


def validate_uploaded_file_security(uploaded_file):
    if uploaded_file is None:
        raise UploadSecurityError("No file was uploaded.")

    filename = uploaded_file.name
    extension = get_file_extension(filename)
    file_size_mb = get_file_size_mb(uploaded_file)

    if extension in BLOCKED_UPLOAD_EXTENSIONS:
        raise UploadSecurityError(
            f"Unsupported file type: {extension}. Please upload a standard .xlsx workbook only."
        )

    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise UploadSecurityError(
            "Invalid file type. FinPlanIQ only accepts .xlsx Excel workbooks."
        )

    if file_size_mb > MAX_UPLOAD_SIZE_MB:
        raise UploadSecurityError(
            f"File is too large ({file_size_mb:.1f} MB). Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB."
        )

    uploaded_file.seek(0)

    return {
        "filename": filename,
        "extension": extension,
        "file_size_mb": round(file_size_mb, 2),
        "validated_at": datetime.utcnow().isoformat(),
        "status": "passed",
    }


def create_security_event(event_type, details):
    safe_details = {
        key: value
        for key, value in details.items()
        if key not in {"raw_data", "file_contents", "financial_data"}
    }

    return {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": safe_details,
    }