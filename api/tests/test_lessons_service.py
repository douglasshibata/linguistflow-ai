from app.lessons.service import build_prompt, sanitize


def test_sanitize_removes_special_chars():
    assert sanitize("foo<script>bar") == "fooscriptbar"


def test_sanitize_keeps_allowed_chars():
    assert sanitize("Hello, world's 2024 - test.") == "Hello, world's 2024 - test."


def test_sanitize_truncates():
    long = "a" * 200
    assert len(sanitize(long)) == 100


def test_sanitize_handles_none():
    assert sanitize(None) == ""
    assert sanitize("") == ""


def test_build_prompt_injects_sanitized_inputs():
    prompt = build_prompt("Past <Tense>", "Foot;ball", "Spanish")
    assert "Past Tense" in prompt
    assert "English" in prompt
    assert "Football" in prompt
    assert "<" not in prompt
    assert ";" not in prompt
