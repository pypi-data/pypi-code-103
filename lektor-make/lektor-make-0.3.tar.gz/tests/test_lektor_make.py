"""Tests."""
import lektor_make

try:
    from unittest.mock import Mock, patch
except ImportError:  # pragma: no cover
    from mock import Mock, patch  # type: ignore


@patch("lektor_make.subprocess")
def test_makeplugin(subprocess):
    # type: (Mock) -> None
    """Test we call make."""
    plugin = lektor_make.MakePlugin(lambda: None, None)  # pragma: no branch
    plugin.on_before_build_all(lambda: None)  # pragma: no branch
    subprocess.Popen.assert_called_with(["make", "lektor"])
    subprocess.Popen().wait.asset_called()
