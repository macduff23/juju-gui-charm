# This file is part of the Juju GUI, which lets users view and manage Juju
# environments within a graphical interface (https://launchpad.net/juju-gui).
# Copyright (C) 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the Juju GUI server applications."""

import unittest

import mock

from guiserver import (
    apps,
    handlers,
)


class AppsTestMixin(object):
    """Base tests and helper methods for applications.

    Subclasses must define a get_app method returning the application.
    """

    def get_url_spec(self, app, pattern):
        """Return the app URL specification with the given regex pattern.

        Return None if the URL specification is not found.
        See tornado.web.URLSpec.
        """
        for spec in app.handlers[0][1]:
            if spec.regex.pattern == pattern:
                return spec
        return None

    def test_debug_enabled(self):
        # Debug mode is enabled if options.debug is True.
        app = self.get_app(debug=True)
        self.assertTrue(app.settings['debug'])

    def test_debug_disabled(self):
        # Debug mode is disabled if options.debug is False.
        app = self.get_app(debug=False)
        self.assertFalse(app.settings['debug'])


class TestServer(AppsTestMixin, unittest.TestCase):

    def get_app(self, **kwargs):
        """Create and return the server application.

        Use the options provided in kwargs.
        """
        options_dict = {'apiversion': 'go', 'guiroot': '/my/guiroot/'}
        options_dict.update(kwargs)
        options = mock.Mock(**options_dict)
        with mock.patch('guiserver.apps.options', options):
            return apps.server()

    def test_static_files(self):
        # The Juju GUI static files are correctly served.
        app = self.get_app()
        spec = self.get_url_spec(app, r'^/juju-ui/(.*)$')
        self.assertIsNotNone(spec)
        self.assertIn('path', spec.kwargs)
        self.assertEqual('/my/guiroot/juju-ui', spec.kwargs['path'])

    def test_serving_gui_tests(self):
        # The server can be configured to serve GUI unit tests.
        app = self.get_app(servetests='/my/tests/')
        spec = self.get_url_spec(app, r'^/test/(.*)$')
        self.assertIsNotNone(spec)
        self.assertIn('path', spec.kwargs)
        self.assertEqual('/my/tests/', spec.kwargs['path'])

    def test_not_serving_gui_tests(self):
        # The server can be configured to avoid serving GUI unit tests.
        app = self.get_app(servetests=None)
        spec = self.get_url_spec(app, r'^/test/(.*)$')
        self.assertIsNone(spec)


class TestRedirector(AppsTestMixin, unittest.TestCase):

    def get_app(self, **kwargs):
        """Create and return the server application.

        Use the options provided in kwargs.
        """
        options = mock.Mock(**kwargs)
        with mock.patch('guiserver.apps.options', options):
            return apps.redirector()

    def test_redirect_all(self):
        # Ensure all paths are handled by HttpsRedirectHandler.
        app = self.get_app()
        spec = self.get_url_spec(app, r'.*$')
        self.assertIsNotNone(spec)
        self.assertEqual(spec.handler_class, handlers.HttpsRedirectHandler)
