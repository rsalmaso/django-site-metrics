# Copyright (C) 2009-2016, Kyle Fuller and Mariusz Felisiak
# Copyright (C) 2016-2019, Raffaele Salmaso <raffaele@salmaso.org>
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

from django import template
from django.test import TestCase
from metrics.templatetags.metrics_admin import pie_chart
from metrics.templatetags.metrics_tag import ActiveUserNode, active_users


class RequestAdminPieChart(TestCase):
    def test_pie_chart(self):
        inventory = ['apple', 'lemon', 'apple', 'orange', 'lemon', 'lemon']
        result = pie_chart(inventory)
        self.assertTrue(result.startswith('//chart.googleapis.com/chart?'))
        self.assertIn('chs=440x190', result)

        result = pie_chart(inventory, width=100, height=100)
        self.assertTrue(result.startswith('//chart.googleapis.com/chart?'))
        self.assertIn('chs=100x100', result)


# TODO: It's unused but add a parser: template.debug.DebugParser
class RequestTagActiveUserNodeTest(TestCase):
    def test_syntax_error_bad_args_number(self):
        token = template.base.Token(2, 'active_users foo')
        self.assertRaises(template.TemplateSyntaxError, ActiveUserNode, None, token)

    def test_in_amount_duration_as_varname(self):
        token = template.base.Token(2, 'active_users in 10 minutes as users')
        node = ActiveUserNode(None, token)
        self.assertEqual(node.as_varname, 'users')

    def test_in_amount_duration_as_varname_error_bad_number(self):
        token = template.base.Token(2, 'active_users in foo minutes as user_list')
        self.assertRaises(template.TemplateSyntaxError, ActiveUserNode, None, token)

    def test_as_varname(self):
        token = template.base.Token(2, 'active_users as user_list')
        node = ActiveUserNode(None, token)
        self.assertEqual(node.as_varname, 'user_list')

        token = template.base.Token(2, 'active_users as users')
        node = ActiveUserNode(None, token)
        self.assertEqual(node.as_varname, 'users')

    def test_no_args(self):
        token = template.base.Token(2, 'active_users')
        ActiveUserNode(None, token)

    def test_render(self):
        token = template.base.Token(2, 'active_users')
        node = ActiveUserNode(None, token)
        self.assertEqual('', node.render({}))


class RequestTagActiveUsersTest(TestCase):
    def test_active_users(self):
        token = template.base.Token(2, 'active_users')
        node = active_users(None, token)
        self.assertIsInstance(node, ActiveUserNode)
