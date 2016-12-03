# -*- coding: utf-8 -*-

# Copyright (C) 2016, Raffaele Salmaso <raffaele@salmaso.org>
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

from django.test import TestCase
from metrics import router


class RegexPatternTest(TestCase):
    def test_init(self):
        router.RegexPattern(r'^foo$')

    def test_resolve(self):
        pat = router.RegexPattern(r'^foo$', 'bar')
        name, groups = pat.resolve('foo')
        self.assertEqual(name, 'bar')
        self.assertEqual(groups, {})

    def test_resolve_with_group(self):
        pat = router.RegexPattern(r'^foo(?P<id>\d*)$', 'bar')
        name, groups = pat.resolve('foo1')
        self.assertEqual(name, 'bar')
        self.assertIn('id', groups)
        self.assertEqual(groups['id'], '1')

    def test_cant_resolve(self):
        pat = router.RegexPattern(r'^foo$', 'bar')
        self.assertIsNone(pat.resolve('bar'))


class patternsTest(TestCase):
    def setUp(self):
        self.unkn_pat = r'^foobar$'
        self.pat1 = r'^foo$'
        self.pat2 = r'^bar$'
        self.pats = router.patterns(self.unkn_pat, self.pat1, self.pat2)

    def test_resolve(self):
        pat = self.pats.resolve('foo')
        self.assertEqual(pat, ('', {}))

    def test_cant_resolve(self):
        self.assertEqual(self.unkn_pat, self.pats.resolve('barfoo'))
