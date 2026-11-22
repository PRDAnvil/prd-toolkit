"""The inbox page's Done test on a slow server: the panel's items arrive after the panel opens, as on a busy machine."""
import shutil
import time

import pytest
import test_inbox_page
import test_inbox_server

DELAY = 1.0  # seconds; longer than any fixed wait the driver could take for the panel's load


class SlowItemsInbox(test_inbox_server.Inbox):
    """The test inbox, whose server answers every GET of an area's items DELAY seconds late."""

    def __init__(self, tmp_path):
        super().__init__(tmp_path)
        base = self.server.RequestHandlerClass

        class Slow(base):
            def adoption(self, area, verb, query, body):
                if verb == "items":
                    time.sleep(DELAY)
                super().adoption(area, verb, query, body)

        self.server.RequestHandlerClass = Slow


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_done_right_after_the_last_answer_waits_for_a_slow_load(tmp_path, monkeypatch):
    # the same test, unchanged, against a server that is slow to list the area's items
    monkeypatch.setattr(test_inbox_server, "Inbox", SlowItemsInbox)
    test_inbox_page.test_done_right_after_the_last_answer_is_accepted(tmp_path, monkeypatch)
