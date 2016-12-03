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

from django import template

from ..models import Request

register = template.Library()


class ActiveUserNode(template.Node):
    def __init__(self, parser, token):
        tokens = token.contents.split()
        tag_name = tokens.pop(0)
        self.kwargs = {}

        if not ((len(tokens) == 5) or (len(tokens) == 2) or (len(tokens) == 0)):
            raise template.TemplateSyntaxError('Incorrect amount of arguments in the tag {0!r}'.format(tag_name))

        if (len(tokens) == 5) and (tokens[0] == 'in'):
            tokens.pop(0)  # pop 'in' of tokens
            try:
                self.kwargs[str(tokens.pop(0))] = int(tokens.pop(0))
            except ValueError:
                raise template.TemplateSyntaxError('Invalid arguments for {0!r} template tag.'.format(tag_name))
        else:
            self.kwargs['minutes'] = 15

        if (len(tokens) == 2 and (tokens[0] == 'as')):
            self.as_varname = tokens[1]
        else:
            self.as_varname = 'user_list'

    def render(self, context):
        context[self.as_varname] = Request.objects.active_users(**self.kwargs)
        return ''


@register.tag
def active_users(parser, token):
    '''
    This template tag will get a list of active users based on time,
    if you do not supply a time to the tag, the default of 15 minutes
    will be used. With the 'as' clause you can supply what context
    variable you want the user list to be. There is also a 'in' clause,
    after in you would specify a amount and a duration. Such as 2 hours,
    of 10 minutes.

    Syntax::
        {% active_users in [amount] [duration] as [varname] %}
        {% active_users as [varname] %}
        {% active_users %}

    Example usage::
        {% load request_tag %}
        {% active_users in 10 minutes as user_list %}
        {% for user in user_list %}
            {{ user.username }}
        {% endfor %}
    '''
    return ActiveUserNode(parser, token)
