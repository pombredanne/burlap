#NOTE, experimental, incomplete
import os
import re

from fabric.api import (
    env,
    local,
    put as _put,
    require,
    #run as _run,
    run,
    settings,
    sudo,
    cd,
    task,
)

from fabric.contrib import files

from burlap.common import run, put
from burlap import common

#env.proftpd

env.proftpd_service_commands = {
    common.START:{
        common.FEDORA: 'systemctl start proftpd.service',
        common.UBUNTU: 'service proftpd start',
    },
    common.STOP:{
        common.FEDORA: 'systemctl stop proftpd.service',
        common.UBUNTU: 'service proftpd stop',
    },
    common.DISABLE:{
        common.FEDORA: 'systemctl disable proftpd.service',
        common.UBUNTU: 'chkconfig proftpd off',
    },
    common.ENABLE:{
        common.FEDORA: 'systemctl enable proftpd.service',
        common.UBUNTU: 'chkconfig proftpd on',
    },
    common.RESTART:{
        common.FEDORA: 'systemctl restart proftpd.service',
        common.UBUNTU: 'service proftpd restart; sleep 5',
    },
    common.STATUS:{
        common.FEDORA: 'systemctl status proftpd.service',
        common.UBUNTU: 'service proftpd status',
    },
}

PROFTPD = 'PROFTPD'

common.required_system_packages[PROFTPD] = {
    common.FEDORA: ['proftpd'],
    common.UBUNTU: ['proftpd'],
}

def get_service_command(action):
    os_version = common.get_os_version()
    return env.proftpd_service_commands[action][os_version.distro]

@task
def enable():
    cmd = get_service_command(common.ENABLE)
    print cmd
    sudo(cmd)

@task
def disable():
    cmd = get_service_command(common.DISABLE)
    print cmd
    sudo(cmd)

@task
def start():
    cmd = get_service_command(common.START)
    print cmd
    sudo(cmd)

@task
def stop():
    cmd = get_service_command(common.STOP)
    print cmd
    sudo(cmd)

@task
def restart():
    cmd = get_service_command(common.RESTART)
    print cmd
    sudo(cmd)

@task
def status():
    cmd = get_service_command(common.STATUS)
    print cmd
    sudo(cmd)

def render_paths():
    common.render_remote_paths()

@task
def configure(site=None, full=0, dryrun=0):
    """
    Installs and configures proftpd.
    """
    full = int(full)
    dryrun = int(dryrun)
    
#    from burlap import package
##    assert env.proftpd_erlang_cookie
#    if full:
#        package.install_required(type=package.common.SYSTEM, service=proftpd)
#    
#    #render_paths()
#    
#    params = set() # [(user,vhost)]
#    for site, site_data in common.iter_sites(site=site, renderer=render_paths):
#        print '!'*80
#        print site
#        _settings = common.get_settings(site=site)
#        #print '_settings:',_settings
#        if not _settings:
#            continue
#        print 'proftpd:',_settings.BROKER_USER, _settings.BROKER_VHOST
#        params.add((_settings.BROKER_USER, _settings.BROKER_VHOST))
#    
#    for user, vhost in params:
#        env.proftpd_broker_user = user
#        env.proftpd_broker_vhost = vhost
#        with settings(warn_only=True):
#            cmd = 'proftpdctl add_vhost %(proftpd_broker_vhost)s' % env
#            print cmd
#            if not dryrun:
#                sudo(cmd)
#            cmd = 'proftpdctl set_permissions -p %(proftpd_broker_vhost)s %(proftpd_broker_user)s ".*" ".*" ".*"' % env
#            print cmd
#            if not dryrun:
#                sudo(cmd)

def configure_all(**kwargs):
    kwargs['site'] = common.ALL
    return configure(**kwargs)

common.service_configurators[PROFTPD] = [configure_all]
common.service_restarters[PROFTPD] = [restart]
