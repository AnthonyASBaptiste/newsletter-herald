import sys
import os
from unittest.mock import patch, MagicMock

# Add root directory to sys.path so start_dev can be imported
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import start_dev


def mock_sleep_side_effect():
    calls = 0
    def _sleep(seconds):
        nonlocal calls
        calls += 1
        if calls > 2:
            raise KeyboardInterrupt
    return _sleep


@patch("start_dev.subprocess.Popen")
@patch("start_dev.subprocess.check_call")
def test_start_services_no_shell_true(mock_check_call, mock_popen):
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    mock_popen.return_value = mock_process

    with patch("start_dev.time.sleep", side_effect=mock_sleep_side_effect()):
        try:
            start_dev.start_services()
        except SystemExit:
            pass

    assert mock_popen.call_count == 2

    for call_args in mock_popen.call_args_list:
        args, kwargs = call_args
        assert kwargs.get("shell") is not True, "subprocess.Popen should not use shell=True"
