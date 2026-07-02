from __future__ import annotations

from pathlib import Path

from harness.common.multimodal import build_user_content, image_data_url


def test_image_data_url_uses_file_mime_type(tmp_path: Path) -> None:
    image = tmp_path / "sample.png"
    image.write_bytes(b"fake-image")

    assert image_data_url(image) == "data:image/png;base64,ZmFrZS1pbWFnZQ=="


def test_build_user_content_returns_text_without_image() -> None:
    assert build_user_content("describe this") == "describe this"


def test_build_user_content_adds_openai_image_url(tmp_path: Path) -> None:
    image = tmp_path / "sample.jpg"
    image.write_bytes(b"fake-image")

    content = build_user_content("describe this", image=image, image_detail="low")

    assert content == [
        {"type": "text", "text": "describe this"},
        {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64,ZmFrZS1pbWFnZQ==", "detail": "low"},
        },
    ]
