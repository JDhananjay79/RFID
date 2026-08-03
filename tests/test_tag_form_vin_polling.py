import unittest

from ui.components.tag_form import TagFormFrame


class DummyReader:
    def __init__(self):
        self.connected = True
        self.writes = []

    def is_connected(self):
        return self.connected

    def write_bytes(self, data):
        self.writes.append(data)
        return True


class DummyRoot:
    def __init__(self):
        self.scheduled = []

    def after(self, delay, callback):
        self.scheduled.append((delay, callback))
        return len(self.scheduled)

    def after_cancel(self, job_id):
        self.scheduled = [item for item in self.scheduled if item[0] != job_id]


class TestTagFormVINPolling(unittest.TestCase):
    def _build_form(self):
        form = TagFormFrame.__new__(TagFormFrame)
        form.reader = DummyReader()
        form.get_log_console = lambda: []
        form.root = DummyRoot()
        form.pending_requests = {}
        form.request_counter = 0
        form.vin_polling_job = None
        form.vin_polling_active = False
        form._reader_disconnect_callback = None
        form._register_pending_request = TagFormFrame._register_pending_request.__get__(form, TagFormFrame)
        form._start_vin_polling = TagFormFrame._start_vin_polling.__get__(form, TagFormFrame)
        form._stop_vin_polling = TagFormFrame._stop_vin_polling.__get__(form, TagFormFrame)
        form._schedule_vin_poll = TagFormFrame._schedule_vin_poll.__get__(form, TagFormFrame)
        form._send_vin_poll = TagFormFrame._send_vin_poll.__get__(form, TagFormFrame)
        form._send_vin_read_command = TagFormFrame._send_vin_read_command.__get__(form, TagFormFrame)
        return form

    def test_start_vin_polling_sends_periodic_reads(self):
        form = self._build_form()

        form._start_vin_polling()

        self.assertTrue(form.vin_polling_active)
        self.assertEqual(form.reader.writes[0], bytes.fromhex("24110102C1B223"))
        self.assertEqual(len(form.root.scheduled), 1)

        form._send_vin_poll()

        self.assertEqual(len(form.reader.writes), 2)
        self.assertTrue(form.vin_polling_active)


if __name__ == "__main__":
    unittest.main()
