#!/usr/bin/env python

"""
This is the Probedock probe for py.test
"""


import os
import time


import pytest
import requests

from probedock import ProbeDockReporter


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


def pytest_addoption(parser):
    """
    Adds option to enable probedock reporting

    :param parser: py.test parser
    """
    group = parser.getgroup('terminal reporting')
    group.addoption('--probedock', action='store_true',
                    help='report tests to probedock')


def pytest_configure(config):
    """
    enables probedock if probedock is asked

    :param config: configuration from the parser
    """
    if config.option.probedock:
        try:
            config._probedock = ProbedockReport()
        except FileNotFoundError as e:
            print("Probedock:", e.strerror, ":", e.filename)
            pytest.exit("")
        else:
            # noinspection PyProtectedMember
            config.pluginmanager.register(config._probedock)


def pytest_unconfigure(config):
    """
    removes probedock plugin if it was enabled

    :param config: py.test configuration
    """
    probedock = getattr(config, '_probedock', None)
    if probedock:
        # noinspection PyProtectedMember
        del config._probedock
        config.pluginmanager.unregister(probedock)


class PytestProbeDockTestResult(ProbeDockReporter):
    """
    Py.test probedock test result reporter
    """
    def _get_test_id(self, test):
        """ returns the unique id of the test """
        return test.nodeid

    def _get_test_method(self, test):
        """ returns the method name of the test """
        return test.nodeid.split("::")[-1]

    def _get_test_class(self, test):
        """ returns the class in which the test is defined """
        info = test.nodeid.split("::")
        if len(info) > 2:
            return info[1]
        return None

    def _get_test_module(self, test):
        """ returns the module in which the test is defined """
        return os.path.splitext(test.nodeid.split("::")[0])[0]

    def _get_test_namespace(self, test):
        """ returns the name's complete namespace """
        if self._get_test_class(test):
            return self._get_test_package(test) + "." + self._get_test_class(test)
        else:
            return self._get_test_package(test)


class ProbedockReport:
    """
    Probedock reporter for tests run with py.test
    """
    def __init__(self):
        self.reporter = PytestProbeDockTestResult("py.test")
        self.info = None
        self.start_time = None
        self.sent = False

    def pytest_runtest_logreport(self, report):
        """
        saves the test for reporting

        :param report: report of the test
        """
        if report.passed:
            if report.when == 'call':
                self.reporter.addSuccess(report, report.duration)
        if report.failed:
            if report.when != "call":
                self.reporter.addError(report, report.duration, str(report.longrepr))
            elif hasattr(report, "wasxfail"):
                self.reporter.addUnexpectedSuccess(report, report.duration)
            else:
                self.reporter.addFailure(report, report.duration, str(report.longrepr))
        elif report.skipped:
            if hasattr(report, "wasxfail"):
                self.reporter.addExpectedFailure(report, report.duration, str(report.longrepr))
            else:
                # TODO : do something about the "why"
                self.reporter.addSkip(report, report.duration, None)

    # noinspection PyUnusedLocal
    def pytest_sessionstart(self, session):
        """
        Records the starting time for the session

        :param session: test session
        """
        self.start_time = time.time()

    # noinspection PyUnusedLocal
    def pytest_sessionfinish(self, session):
        """
        Sends the data to the probedock server

        :param session: test session
        """
        # TODO check that the tests were run without errors before sending them
        try:
            self.info = self.reporter.send_report(time.time() - self.start_time)
        except requests.exceptions.ConnectionError as e:
            self.info = "Error connecting to {}. Couldn't send data".format(e.request.url)
        else:
            self.sent = True

    def pytest_terminal_summary(self, terminalreporter):
        """
        prints information about reporting data to Probedock

        :param terminalreporter: reporter
        """
        terminalreporter.write_sep("=", "Sending information to Probedock".format(self.info))
        if self.sent:
            terminalreporter.write_line("Data sent to {}".format(self.info))
        else:
            terminalreporter.write_line(self.info)
