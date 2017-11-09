# Copyright 2015 Brocade Communications System, Inc.
#
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

from __future__ import absolute_import

from django.conf import settings
from oslo_log import log as logging
from apmecclient.v1_0 import client as apmec_client

from horizon.utils.memoized import memoized  # noqa
from openstack_dashboard.api import base


LOG = logging.getLogger(__name__)


@memoized
def apmecclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    c = apmec_client.Client(
        token=request.user.token.id,
        auth_url=base.url_for(request, 'identity'),
        endpoint_url=base.url_for(request, 'mec-orchestration'),
        insecure=insecure, ca_cert=cacert)
    return c


def mea_list(request, **params):
    LOG.debug("mea_list(): params=%s", params)
    meas = apmecclient(request).list_meas(**params).get('meas')
    return meas


def mead_list(request, **params):
    LOG.debug("mead_list(): params=%s", params)
    meads = apmecclient(request).list_meads(**params).get('meads')
    return meads


def create_mead(request, tosca_body=None, **params):
    LOG.debug("create_mead(): params=%s", params)
    mead_instance = apmecclient(request).create_mead(body=tosca_body)
    return mead_instance


def create_mea(request, mea_arg, **params):
    LOG.debug("create_mea(): mea_arg=%s", str(mea_arg))
    mea_instance = apmecclient(request).create_mea(body=mea_arg)
    return mea_instance


def get_mead(request, mead_id):
    LOG.debug("mead_get(): mead_id=%s", str(mead_id))
    mead = apmecclient(request).show_mead(mead_id)
    return mead


def get_mea(request, mea_id):
    LOG.debug("mea_get(): mea_id=%s", str(mea_id))
    mea_instance = apmecclient(request).show_mea(mea_id)
    return mea_instance


def delete_mea(request, mea_id):
    LOG.debug("delete_mea():mea_id=%s", str(mea_id))
    apmecclient(request).delete_mea(mea_id)


def delete_mead(request, mead_id):
    LOG.debug("delete_mead():mead_id=%s", str(mead_id))
    apmecclient(request).delete_mead(mead_id)


def create_vim(request, vim_arg):
    LOG.debug("create_vim(): vim_arg=%s", str(vim_arg))
    vim_instance = apmecclient(request).create_vim(body=vim_arg)
    return vim_instance


def get_vim(request, vim_id):
    LOG.debug("vim_get(): vim_id=%s", str(vim_id))
    vim_instance = apmecclient(request).show_vim(vim_id)
    return vim_instance


def delete_vim(request, vim_id):
    LOG.debug("delete_vim():vim_id=%s", str(vim_id))
    apmecclient(request).delete_vim(vim_id)


def vim_list(request, **params):
    LOG.debug("vim_list(): params=%s", params)
    vims = apmecclient(request).list_vims(**params).get('vims')
    return vims


def events_list(request, resource_id):
    params = {'resource_id': resource_id}
    events = apmecclient(request).list_events(**params).get('events')
    LOG.debug("events_list() params=%s events=%s l=%s", params, events,
              len(events))
    return events


def nfy_list(request, **params):
    LOG.debug("nfy_list(): params=%s", params)
    nfys = apmecclient(request).list_nfys(**params).get('nfys')
    return nfys


def nfyd_list(request, **params):
    LOG.debug("nfyd_list(): params=%s", params)
    nfyds = apmecclient(request).list_nfyds(**params).get('nfyds')
    return nfyds


def create_nfyd(request, tosca_body=None, **params):
    LOG.debug("create_nfyd(): params=%s", params)
    nfyd_instance = apmecclient(request).create_nfyd(body=tosca_body)
    return nfyd_instance


def create_nfy(request, nfy_arg, **params):
    LOG.debug("create_nfy(): mea_arg=%s", str(nfy_arg))
    nfy_instance = apmecclient(request).create_nfy(body=nfy_arg)
    return nfy_instance


def get_nfyd(request, nfyd_id):
    LOG.debug("nfyd_get(): nfyd_id=%s", str(nfyd_id))
    nfyd = apmecclient(request).show_nfyd(nfyd_id)
    return nfyd


def get_nfy(request, nfy_id):
    LOG.debug("nfy_get(): nfy_id=%s", str(nfy_id))
    nfy_instance = apmecclient(request).show_nfy(nfy_id)
    return nfy_instance


def delete_nfy(request, nfy_id):
    LOG.debug("delete_nfy():nfy_id=%s", str(nfy_id))
    apmecclient(request).delete_nfy(nfy_id)


def delete_nfyd(request, nfyd_id):
    LOG.debug("delete_nfyd():nfyd_id=%s", str(nfyd_id))
    apmecclient(request).delete_nfyd(nfyd_id)


def create_nsd(request, tosca_body=None, **params):
    LOG.debug("create_nsd(): params=%s", params)
    nsd_instance = apmecclient(request).create_nsd(body=tosca_body)
    return nsd_instance


def nsd_list(request, **params):
    LOG.debug("nsd_list(): params=%s", params)
    nsds = apmecclient(request).list_nsds(**params).get('nsds')
    return nsds


def get_nsd(request, nsd_id):
    LOG.debug("nsd_get(): nsd_id=%s", str(nsd_id))
    nsd = apmecclient(request).show_nsd(nsd_id)
    return nsd


def delete_nsd(request, nsd_id):
    LOG.debug("delete_nsd():nsd_id=%s", str(nsd_id))
    apmecclient(request).delete_nsd(nsd_id)


def get_ns(request, ns_id):
    LOG.debug("ns_get(): ns_id=%s", str(ns_id))
    ns_instance = apmecclient(request).show_ns(ns_id)
    return ns_instance


def delete_ns(request, ns_id):
    LOG.debug("delete_ns():ns_id=%s", str(ns_id))
    apmecclient(request).delete_ns(ns_id)


def ns_list(request, **params):
    LOG.debug("ns_list(): params=%s", params)
    nss = apmecclient(request).list_nss(**params).get('nss')
    return nss


def create_ns(request, ns_arg, **params):
    LOG.debug("create_ns(): ns_arg=%s", str(ns_arg))
    ns_instance = apmecclient(request).create_ns(body=ns_arg)
    return ns_instance
