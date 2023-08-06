#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_seqlog
----------------------------------

Tests for `seqlog.consumer.QueueConsumer` module.
"""
import logging
from queue import Queue
from threading import Event
from time import sleep

import seqlog

from seqlog.structured_logging import StructuredLogRecord

from seqlog import SeqLogHandler
from seqlog.consumer import QueueConsumer


class TestLogRecordConsumer(object):

    def test_callable_failures(self):
        lh = SeqLogHandler('localhost')
        le = StructuredLogRecord('test', logging.INFO, '/dev/null', 1, 'Hello world!', (), None)
        callable_called = False

        def handle_failure(e):
            nonlocal callable_called
            callable_called = True

        seqlog.set_callback_on_failure(handle_failure)

        lh.publish_log_batch([le])
        assert callable_called
    #
    # Without flush timeout
    #
    def test_batchsize_2_pre_fill(self):
        record_queue = Queue()
        record_queue.put("Item1")
        record_queue.put("Item2")

        batch_received = Event()

        def handler(record_batch):
            assert len(record_batch) == 2, \
                "Incorrect batch size (expected 2, but found {}.".format(len(record_batch))

            batch_received.set()

        consumer = QueueConsumer("Test Consumer", record_queue, handler, batch_size=2)
        consumer.start()

        batch_received.wait(timeout=2000)

        consumer.stop()

    def test_batchsize_2_post_fill(self):
        record_queue = Queue()

        batch_received = Event()

        def handler(record_batch):
            assert len(record_batch) == 2, \
                "Incorrect batch size (expected 2, but found {}.".format(len(record_batch))

            batch_received.set()

        consumer = QueueConsumer("Test Consumer", record_queue, handler, batch_size=2)
        consumer.start()

        record_queue.put("Item1")
        record_queue.put("Item2")

        batch_received.wait(timeout=2000)

        consumer.stop()

    #
    # With flush timeout
    #
    def test_batchsize_3_post_fill_flush_timeout(self):
        record_queue = Queue()

        batch_received = Event()

        def handler(record_batch):
            assert len(record_batch) == 2, \
                "Incorrect batch size (expected 2, but found {}.".format(len(record_batch))

            batch_received.set()

        consumer = QueueConsumer("Test Consumer", record_queue, handler, batch_size=3, auto_flush_timeout=0.2)
        consumer.start()

        record_queue.put("Item1")
        record_queue.put("Item2")
        sleep(300 / 1000)
        record_queue.put("Item3")

        batch_received.wait(timeout=2000)

        consumer.stop()
