import pytest

@pytest.fixture
def empty_fixture():
    pass


def test_demo(empty_fixture):
    assert False