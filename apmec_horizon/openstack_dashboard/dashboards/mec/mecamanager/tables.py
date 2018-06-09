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


from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import messages
from horizon import tables

from openstack_dashboard import policy
from apmec_horizon.openstack_dashboard import api
from apmecclient.common.exceptions import NotFound


class MECAManagerItem(object):
    def __init__(self, name, description, vim, status,
                 meca_id, error_reason):
        self.name = name
        self.description = description
        self.vim = vim
        self.status = status
        self.id = meca_id
        self.error_reason = error_reason


class MECAManagerItemList(object):
    MECALIST_P = []

    @classmethod
    def get_obj_given_stack_ids(cls, meca_id):
        for obj in cls.MECALIST_P:
            if obj.id == meca_id:
                return obj

    @classmethod
    def add_item(cls, item):
        cls.MECALIST_P.append(item)

    @classmethod
    def clear_list(cls):
        cls.MECALIST_P = []


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class MECAUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.status != 'DELETE_COMPLETE'

    def get_data(self, request, meca_id):
        try:
            # stack = api.heat.stack_get(request, stack_id)
            # if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
            #    raise Http404
            item = MECAManagerItemList.get_obj_given_stack_ids(meca_id)
            meca_instance = api.apmec.get_meca(request, meca_id)

            if not meca_instance and not item:
                # TODO(NAME) - bail with error
                return None

            if not meca_instance and item:
                # API failure, just keep the current state
                return item

            meca = meca_instance['meca']
            try:
                meca_desc_str = meca['description']
            except KeyError:
                meca_desc_str = ""

            vim = meca['vim_id']
            if not item:
                # Add an item entry
                item = MECAManagerItem(meca['name'], meca_desc_str,
                                     str(vim),
                                     meca['status'], meca['id'],
                                     meca['error_reason'])
            else:
                item.description = meca_desc_str
                item.status = meca['status']
                item.id = meca['id']
            return item
        except (Http404, NotFound):
            raise Http404
        except Exception as e:
            messages.error(request, e)
            raise


class DeleteMECA(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Terminate MECA",
            u"Terminate MECAs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Terminate MECA",
            u"Terminate MECAs",
            count
        )

    def action(self, request, obj_id):
        api.apmec.delete_meca(request, obj_id)


class DeployMECA(tables.LinkAction):
    name = "deploymeca"
    verbose_name = _("Deploy MECA")
    classes = ("ajax-modal",)
    icon = "plus"
    url = "horizon:mec:mecamanager:deploymeca"


class MECAManagerTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("ERROR", False),
    )
    name = tables.Column("name",
                         link="horizon:mec:mecamanager:detail",
                         verbose_name=_("MECA Name"))
    description = tables.Column("description",
                                verbose_name=_("Description"))
    vim = tables.Column("vim", verbose_name=_("VIM"))
    status = tables.Column("status",
                           status=True,
                           status_choices=STATUS_CHOICES)
    error_reason = tables.Column("error_reason",
                                 verbose_name=_("Error Reason"))

    class Meta(object):
        name = "mecamanager"
        verbose_name = _("MECAManager")
        status_columns = ["status", ]
        row_class = MECAUpdateRow
        table_actions = (DeployMECA, DeleteMECA, MyFilterAction,)
