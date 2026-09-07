import tkinter as tk
from unittest.mock import Mock

import pytest

from app.ui.application_dialog import ApplicationDialog


def test_modal_waits_until_visible_before_grab_and_focus():
    calls = []
    dialog = Mock()
    dialog.wait_visibility.side_effect = lambda: calls.append("visible")
    dialog.lift.side_effect = lambda: calls.append("lift")
    dialog.grab_set.side_effect = lambda: calls.append("grab")
    company_entry = Mock()
    company_entry.focus_set.side_effect = lambda: calls.append("focus")
    dialog._entries = {"company": company_entry}

    ApplicationDialog._activate_modal(dialog)

    assert calls == ["visible", "lift", "grab", "focus"]


def test_modal_activation_error_closes_dialog():
    dialog = Mock()
    dialog.wait_visibility.return_value = None
    dialog.grab_set.side_effect = tk.TclError("grab failed")
    dialog._close = Mock()

    with pytest.raises(tk.TclError, match="grab failed"):
        ApplicationDialog._activate_modal(dialog)

    dialog._close.assert_called_once_with()


def test_close_releases_only_its_own_grab():
    dialog = Mock()
    dialog.grab_current.return_value = dialog

    ApplicationDialog._close(dialog)

    dialog.grab_release.assert_called_once_with()
    dialog.destroy.assert_called_once_with()
