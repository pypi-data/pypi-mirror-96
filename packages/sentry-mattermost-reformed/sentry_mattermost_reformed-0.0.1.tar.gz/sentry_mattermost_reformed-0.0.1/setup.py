# Copyright (c) 2015 NDrive SA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from setuptools import setup
from sentry_mattermost_reformed import VERSION

setup(
    name="sentry_mattermost_reformed",
    version=VERSION,
    author="Mohammad Hadi Azaddel",
    author_email="m.h.azaddel@gmail.com",
    description=("A Sentry plugin to send Mattermost notifications."),
    license="MIT",
    keywords="sentry mattermost devops",
    url="https://github.com/hadi2f244/sentry-mattermost-reformed",
    packages=['sentry_mattermost_reformed'],
    entry_points={
       'sentry.plugins': [
            'mattermost = sentry_mattermost_reformed.plugin:Mattermost'
        ],
    },
)
