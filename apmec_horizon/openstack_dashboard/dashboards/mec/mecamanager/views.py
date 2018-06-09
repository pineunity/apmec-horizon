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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from oslo_log import log as logging

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized

from apmec_horizon.openstack_dashboard import api as apmec_api
from apmec_horizon.openstack_dashboard.dashboards.mec.mecamanager \
    import forms as project_forms

from apmec_horizon.openstack_dashboard.dashboards.mec.mecamanager \
    import tabs as mec_tabs

LOG = logging.getLogger(__name__)


class IndexView(tabs.TabbedTableView):
    # A very simple class-based view...
    tab_group_class = mec_tabs.MECAManagerTabs
    template_name = 'mec/mecamanager/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class DeployMECAView(forms.ModalFormView):
    form_class = project_forms.DeployMECA
    template_name = 'mec/mecamanager/deploy_meca.html'
    success_url = reverse_lazy("horizon:mec:mecamanager:index")
    modal_id = "deploy_meca_modal"
    modal_header = _("Deploy MECA")
    submit_label = _("Deploy MECA")
    submit_url = "horizon:mec:mecamanager:deploymeca"

    def get_initial(self):
        # return {"instance_id": self.kwargs["instance_id"]}
        return {}

    def get_context_data(self, **kwargs):
        context = super(DeployMECAView, self).get_context_data(**kwargs)
        # instance_id = self.kwargs['instance_id']
        # context['instance_id'] = instance_id
        # context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url)
        return context


class DetailView(tabs.TabView):
    tab_group_class = mec_tabs.MECADetailsTabs
    template_name = 'mec/mecamanager/detail.html'
    redirect_url = 'horizon:mec:mecamanager:index'
    page_title = _("MECA Details: {{ meca_id }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        meca = self.get_data()
        context['meca'] = meca
        context['meca_id'] = kwargs['meca_id']
        context['url'] = reverse(self.redirect_url)
        return context

    @memoized.memoized_method
    def get_data(self):
        meca_id = self.kwargs['meca_id']

        try:
            meca = apmec_api.apmec.get_meca(self.request, meca_id)
            return meca
        except ValueError as e:
            msg = _('Cannot decode json : %s') % e
            LOG.error(msg)
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'MECA "%s".') % meca_id,
                              redirect=redirect)
            raise exceptions.Http302(redirect)

    def get_tabs(self, request, *args, **kwargs):
        meca = self.get_data()
        return self.tab_group_class(request, meca=meca, **kwargs)
