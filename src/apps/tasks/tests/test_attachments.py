from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.tasks.models import (
    MAX_EXECUTION_ATTACHMENT_SIZE,
    validate_execution_attachment,
)


def make_png_upload(name="evidence.png"):
    image_buffer = BytesIO()
    Image.new("RGB", (2, 2), color="white").save(image_buffer, format="PNG")
    return SimpleUploadedFile(name, image_buffer.getvalue(), content_type="image/png")


def test_execution_attachment_accepts_valid_pdf():
    upload = SimpleUploadedFile(
        "evidence.pdf",
        b"%PDF-1.4\nValid PDF content\n%%EOF",
        content_type="application/pdf",
    )

    validate_execution_attachment(upload)

    assert upload.tell() == 0


def test_execution_attachment_accepts_valid_png():
    upload = make_png_upload()

    validate_execution_attachment(upload)

    assert upload.tell() == 0


def test_execution_attachment_rejects_files_over_size_limit():
    upload = SimpleUploadedFile(
        "large.pdf",
        b"x" * (MAX_EXECUTION_ATTACHMENT_SIZE + 1),
        content_type="application/pdf",
    )

    with pytest.raises(ValidationError, match="no máximo 10 MB"):
        validate_execution_attachment(upload)


def test_execution_attachment_rejects_unsupported_extensions():
    upload = SimpleUploadedFile(
        "evidence.txt",
        b"plain text",
        content_type="text/plain",
    )

    with pytest.raises(ValidationError, match="JPG/PNG ou um arquivo PDF"):
        validate_execution_attachment(upload)


def test_execution_attachment_rejects_invalid_pdf_content():
    upload = SimpleUploadedFile(
        "evidence.pdf",
        b"not a pdf",
        content_type="application/pdf",
    )

    with pytest.raises(ValidationError, match="PDF válido"):
        validate_execution_attachment(upload)


def test_execution_attachment_rejects_image_with_mismatched_extension():
    upload = make_png_upload("evidence.jpg")

    with pytest.raises(ValidationError, match="não corresponde"):
        validate_execution_attachment(upload)
