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

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs

from apmec_horizon.openstack_dashboard import api
from apmec_horizon.openstack_dashboard.dashboards.mec.mecamanager import tables
from apmec_horizon.openstack_dashboard.dashboards.mec import utils


class MECAManagerTab(tabs.TableTab):
    name = _("MECAManager Tab")
    slug = "mecamanager_tab"
    table_classes = (tables.MECAManagerTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_mecamanager_data(self):
        try:
            self._has_more = True
            tables.MECAManagerItemList.clear_list()
            mecas = api.apmec.meca_list(self.request)
            for meca in mecas:
                try:
                    meca_desc_str = meca['description']
                except KeyError:
                    meca_desc_str = ""

                vim = meca['vim_id']
                obj = tables.MECAManagerItem(
                    meca['name'],
                    meca_desc_str,
                    vim,
                    meca['status'],
                    meca['id'],
                    meca['error_reason'])
                tables.MECAManagerItemList.add_item(obj)
            return tables.MECAManagerItemList.MECALIST_P
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


class MECAManagerTabs(tabs.TabGroup):
    slug = "mecamanager_tabs"
    tabs = (MECAManagerTab,)
    sticky = True


class MECAEventsTab(tabs.TableTab):
    name = _("Events Tab")
    slug = "events_tab"
    table_classes = (utils.EventsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_events_data(self):
        try:
            self._has_more = True
            utils.EventItemList.clear_list()
            events = api.apmec.events_list(self.request,
                                            self.tab_group.kwargs['meca_id'])
            for event in events:
                evt_obj = utils.EventItem(
                    event['id'], event['resource_state'],
                    event['event_type'],
                    event['timecatamp'],
                    event['event_details'])
                utils.EventItemList.add_item(evt_obj)
            return utils.EventItemList.EVTLIST_P
        except Exception as e:
            self._has_more = False
            error_message = _('Unable to get events %s') % e
            exceptions.handle(self.request, error_message)
            return []


class MECADetailsTabs(tabs.TabGroup):
    slug = "MECA_details"
    tabs = (MECAEventsTab,)
    sticky = True
