import pytest

@pytest.fixture(scope="function")
def func_fixture():
    """A function-scoped fixture."""
    return "function"

@pytest.fixture(scope="module")
def module_fixture():
    """A module-scoped fixture."""
    return "module"

@pytest.fixture(scope="session")
def session_fixture():
    """A session-scoped fixture."""
    return "session"

@pytest.fixture(scope="class")
def class_fixture():
    """A class-scoped fixture."""
    return "class"

@pytest.fixture(scope="package")
def package_fixture():
    """A package-scoped fixture."""
    return "package"

def test_example(func_fixture, module_fixture, session_fixture, class_fixture, package_fixture):
    """Test that uses all fixtures."""
    pass