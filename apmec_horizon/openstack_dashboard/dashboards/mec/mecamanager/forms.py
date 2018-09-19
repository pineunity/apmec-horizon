# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from oslo_log import log as logging

from horizon import exceptions
from horizon import forms
from horizon import messages

from apmec_horizon.openstack_dashboard import api

LOG = logging.getLogger(__name__)


class DeployMECA(forms.SelfHandlingForm):
    mca_name = forms.CharField(max_length=255, label=_("MECA Name"))
    description = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'rows': 4}),
                                  label=_("Description"),
                                  required=False)
    mcad_id = forms.ChoiceField(label=_("MECA Catalog Name"))
    vim_id = forms.ChoiceField(label=_("VIM Name"), required=False)
    source_type = forms.ChoiceField(
        label=_('Parameter Value Source'),
        required=False,
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'source'}))

    param_file = forms.FileField(
        label=_('Parameter Value File'),
        help_text=_('A local Parameter Value file to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-file': _('Parameter Value File')}),
        required=False)

    direct_input = forms.CharField(
        label=_('Parameter Value YAML'),
        help_text=_('The YAML formatted contents of Parameter Values.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'source',
                   'data-source-raw': _('Parameter Values')}),
        required=False)

    config_type = forms.ChoiceField(
        label=_('Configuration Value Source'),
        required=False,
        choices=[('file', _('File')),
                 ('raw', _('Direct Input'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'config'}))

    config_file = forms.FileField(
        label=_('Configuration Value File'),
        help_text=_('MECA Configuration file with YAML '
                    'formatted contents to upload.'),
        widget=forms.FileInput(
            attrs={'class': 'switched', 'data-switch-on': 'config',
                   'data-config-file': _('Configuration Value File')}),
        required=False)

    config_input = forms.CharField(
        label=_('Configuration Value YAML'),
        help_text=_('YAML formatted MECA configuration text.'),
        widget=forms.widgets.Textarea(
            attrs={'class': 'switched', 'data-switch-on': 'config',
                   'data-config-raw': _('Configuration Values')}),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(DeployMECA, self).__init__(request, *args, **kwargs)

        try:
            mecad_list = api.apmec.mecad_list(request)
            available_choices_mecad = [(meca['id'], meca['name']) for meca in
                                     mecad_list]
        except Exception as e:
            available_choices_mecad = []
            msg = _('Failed to retrieve available MECA Catalog nameca: %s') % e
            LOG.error(msg)

        try:
            vim_list = api.apmec.vim_list(request)
            available_choices_vims = [(vim['id'], vim['name']) for vim in
                                      vim_list]

        except Exception as e:
            available_choices_vims = []
            msg = _('Failed to retrieve available VIM nameca: %s') % e
            LOG.error(msg)

        self.fields['mecad_id'].choices = [('', _('Select a MECA Catalog Name'))
                                         ]+available_choices_mecad
        self.fields['vim_id'].choices = [('',
                                          _('Select a VIM Name'))
                                         ]+available_choices_vims

    def clean(self):
        data = super(DeployMECA, self).clean()

        param_file = data.get('param_file', None)
        param_raw = data.get('direct_input', None)

        if param_raw and param_file:
            raise ValidationError(
                _("Cannot specify both file and direct input."))

        if param_file and not param_file.name.endswith('.yaml'):
            raise ValidationError(
                _("Please upload .yaml file only."))

        if param_file:
            data['param_values'] = self.files['param_file'].read()
        elif param_raw:
            data['param_values'] = data['direct_input']
        else:
            data['param_values'] = None

        config_file = data.get('config_file', None)
        config_raw = data.get('config_input', None)

        if config_file and config_raw:
            raise ValidationError(
                _("Cannot specify both file and direct input."))

        if config_file and not config_file.name.endswith('.yaml'):
            raise ValidationError(_("Only .yaml file uploads supported"))

        if config_file:
            data['config_values'] = self.files['config_file'].read()
        elif config_raw:
            data['config_values'] = data['config_input']
        else:
            data['config_values'] = None

        return data

    def handle(self, request, data):
        try:
            meca_name = data['meca_name']
            description = data['description']
            mecad_id = data['mecad_id']
            vim_id = data['vim_id']
            param_val = data['param_values']
            config_val = data['config_values']
            meca_arg = {'meca': {'mecad_id': mecad_id, 'name':  meca_name,
                             'description': description,
                             'vim_id': vim_id}}
            meca_attr = meca_arg['meca'].setdefault('attributes', {})
            if param_val:
                meca_attr['param_values'] = param_val
            if config_val:
                meca_attr['config'] = config_val

            api.apmec.create_meca(request, meca_arg)
            messages.success(request,
                             _('MECA %s create operation initiated.') %
                             meca_name)
            return True
        except Exception as e:
            exceptions.handle(request,
                              _('Failed to create MECA: %s') %
                              e.message)
