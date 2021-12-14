import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(scope="class")
def mock_env_simple(request):
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv("H1ST_ENGINE", "h1st.engines.simple.SimpleExecutionEngine")

