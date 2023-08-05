# Copyright 2011 OpenStack Foundation
# Copyright 2013 Rackspace Hosting
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# Copyright 2013 Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# -*- coding: utf-8 -*-

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

sys.path.insert(0, ROOT)
sys.path.insert(0, BASE_DIR)

extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'openstackdocstheme',
    'sphinxcontrib.apidoc',
]

# sphinxcontrib.apidoc options
apidoc_module_dir = '../../troveclient'
apidoc_output_dir = 'reference/api'
apidoc_excluded_paths = [
    'compat/tests/*',
    'compat/tests',
    'tests/*',
    'tests']
apidoc_separate_modules = True

# openstackdocstheme options
openstackdocs_repo_name = 'openstack/python-troveclient'
openstackdocs_bug_project = 'python-troveclient'
openstackdocs_bug_tag = ''
html_theme = 'openstackdocs'

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

copyright = '2014, OpenStack Foundation'

exclude_trees = []

pygments_style = 'native'

htmlhelp_basename = 'python-troveclientdoc'
latex_documents = [
    ('index', 'python-troveclient.tex', 'python-troveclient Documentation',
     'OpenStack', 'manual'),
]
