# Copyright (C) 2016-2018, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2016, Kyle Fuller and Mariusz Felisiak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY KYLE FULLER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KYLE FULLER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import mock
from django.core import exceptions
from django.test import TestCase
from metrics import traffic
from metrics.models import Request


class ModulesLoadTest(TestCase):
    def setUp(self):
        self.modules = traffic.Modules()

    def test_load(self):
        self.modules.load()
        for mod in self.modules._modules:
            self.assertIsInstance(mod, traffic.Module)

    @mock.patch('metrics.settings.TRAFFIC_MODULES',
                ('foobar',))
    def test_bad_module(self):
        self.assertRaises(exceptions.ImproperlyConfigured, self.modules.load)

    @mock.patch('metrics.settings.TRAFFIC_MODULES',
                ('foo.bar',))
    def test_import_error(self):
        self.assertRaises(exceptions.ImproperlyConfigured, self.modules.load)

    @mock.patch('metrics.settings.TRAFFIC_MODULES',
                ('metrics.traffic.Foo',))
    def test_module_not_exists(self):
        self.assertRaises(exceptions.ImproperlyConfigured, self.modules.load)


class ModulesModulesTest(TestCase):
    def setUp(self):
        self.modules = traffic.Modules()

    def test_loaded(self):
        self.modules.load()
        modules = self.modules.modules
        self.assertIsInstance(modules, tuple)

    def test_unloaded(self):
        modules = self.modules.modules
        self.assertIsInstance(modules, tuple)


class ModulesTableTest(TestCase):
    def setUp(self):
        self.modules = traffic.Modules()

    def test_table(self):
        queries = Request.objects.all()
        table = self.modules.table(queries)
        self.assertIsInstance(table, tuple)


class ModulesGraphTest(TestCase):
    def setUp(self):
        self.modules = traffic.Modules()

    def test_graph(self):
        queries = Request.objects.all()
        table = self.modules.graph(queries)
        self.assertIsInstance(table, tuple)


class ModuleBaseTest(TestCase):
    def test_init(self):
        traffic.Module()


class ModuleAjaxTest(TestCase):
    def test_count(self):
        module = traffic.Ajax()
        queries = Request.objects.all()
        module.count(queries)


class ModuleNotAjaxTest(TestCase):
    def test_count(self):
        module = traffic.NotAjax()
        queries = Request.objects.all()
        module.count(queries)


class ModuleErrorTest(TestCase):
    def test_count(self):
        module = traffic.Error()
        queries = Request.objects.all()
        module.count(queries)


class ModuleError404Test(TestCase):
    def test_count(self):
        module = traffic.Error404()
        queries = Request.objects.all()
        module.count(queries)


class ModuleHitTest(TestCase):
    def test_count(self):
        module = traffic.Hit()
        queries = Request.objects.all()
        module.count(queries)


class ModuleSearchTest(TestCase):
    def test_count(self):
        module = traffic.Search()
        queries = Request.objects.all()
        module.count(queries)


class ModuleSecureTest(TestCase):
    def test_count(self):
        module = traffic.Secure()
        queries = Request.objects.all()
        module.count(queries)


class ModuleUnsecureTest(TestCase):
    def test_count(self):
        module = traffic.Unsecure()
        queries = Request.objects.all()
        module.count(queries)


class ModuleUniqueVisitTest(TestCase):
    def test_count(self):
        module = traffic.UniqueVisit()
        queries = Request.objects.all()
        module.count(queries)


class ModuleUniqueVisitorTest(TestCase):
    def test_count(self):
        module = traffic.UniqueVisitor()
        queries = Request.objects.all()
        module.count(queries)


class ModuleUserTest(TestCase):
    def test_count(self):
        module = traffic.User()
        queries = Request.objects.all()
        module.count(queries)


class ModuleUniqueUserTest(TestCase):
    def test_count(self):
        module = traffic.UniqueUser()
        queries = Request.objects.all()
        module.count(queries)
