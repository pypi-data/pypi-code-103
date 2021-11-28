# MIT License
#
# Copyright (c) 2020 Jonathan Zernik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
import threading

logger = logging.getLogger(__name__)


class ProcessReceivedPaymentsWorker:
    def __init__(self, payment_processor):
        self.payment_processor = payment_processor
        self.stopped = threading.Event()

    def start_running(self):
        threading.Thread(
            target=self.process_subscribed_invoices,
            # daemon=True,
            name="process_received_payments_thread",
        ).start()

    def stop_running(self):
        self.stopped.set()

    def process_subscribed_invoices(self):
        logger.info("Starting ProcessReceivedPaymentsWorker...")
        self.payment_processor.start_processing()
        self.stopped.wait()
        logger.info("Stopping ProcessReceivedPaymentsWorker...")
        self.payment_processor.stop_processing()
