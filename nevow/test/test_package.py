# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""Smoke tests for the trimmed Beremiz-focused package surface."""

import importlib

from twisted.trial.unittest import SynchronousTestCase

class RuntimeSurfaceTests(SynchronousTestCase):
    def test_runtimeModulesImport(self):
        importlib.import_module("nevow.appserver")
        importlib.import_module("nevow.loaders")
        importlib.import_module("nevow.rend")
        importlib.import_module("nevow.static")
        importlib.import_module("nevow.tags")
        importlib.import_module("nevow.url")
        importlib.import_module("formless.annotate")
        importlib.import_module("formless.configurable")
        importlib.import_module("formless.webform")


class RemovedFeatureTests(SynchronousTestCase):
    def test_athenaModuleMissing(self):
        self.assertRaises(ImportError, importlib.import_module, "nevow.athena")


    def test_nitScriptModuleMissing(self):
        self.assertRaises(
            ImportError, importlib.import_module, "nevow.scripts.nit")


    def test_livetrialModuleMissing(self):
        self.assertRaises(
            ImportError, importlib.import_module, "nevow.livetrial.runner")


    def test_canvasModuleMissing(self):
        self.assertRaises(ImportError, importlib.import_module, "nevow.canvas")


    def test_guardModuleMissing(self):
        self.assertRaises(ImportError, importlib.import_module, "nevow.guard")


    def test_i18nModuleMissing(self):
        self.assertRaises(ImportError, importlib.import_module, "nevow.i18n")
