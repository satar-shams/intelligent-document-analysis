from unittest.mock import Mock


def test_fake_llm_returns_fixed_response():
    fake_llm = Mock()
    fake_llm.generate.return_value = "FAKE ANSWER"

    result = fake_llm.generate(prompt="Anything")

    assert isinstance(result, str)
    assert result.strip() != ""
    assert result == "FAKE ANSWER"