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

env.rabbitmq_host = "localhost"
env.rabbitmq_vhost = "/"
env.rabbitmq_erlang_cookie = ''
env.rabbitmq_nodename = "rabbit"
env.rabbitmq_user = "guest"
env.rabbitmq_password = "guest"
env.rabbitmq_node_ip_address = ''
env.rabbitmq_port = 5672
env.rabbitmq_erl_args = ""
env.rabbitmq_cluster = "no"
env.rabbitmq_cluster_config = "/etc/rabbitmq/rabbitmq_cluster.config"
env.rabbitmq_logdir = "/var/log/rabbitmq"
env.rabbitmq_mnesiadir = "/var/lib/rabbitmq/mnesia"
env.rabbitmq_start_args = ""
env.rabbitmq_erlang_cookie_template = ''

env.rabbitmq_service_commands = {
    common.START:{
        common.FEDORA: 'systemctl start rabbitmq-server.service',
        common.UBUNTU: 'service rabbitmq-server start',
    },
    common.STOP:{
        common.FEDORA: 'systemctl stop rabbitmq-server.service',
        common.UBUNTU: 'service rabbitmq-server stop',
    },
    common.DISABLE:{
        common.FEDORA: 'systemctl disable rabbitmq-server.service',
        common.UBUNTU: 'chkconfig rabbitmq-server off',
    },
    common.ENABLE:{
        common.FEDORA: 'systemctl enable rabbitmq-server.service',
        common.UBUNTU: 'chkconfig rabbitmq-server on',
    },
    common.RESTART:{
        common.FEDORA: 'systemctl restart rabbitmq-server.service',
        common.UBUNTU: 'service rabbitmq-server restart; sleep 5',
    },
    common.STATUS:{
        common.FEDORA: 'systemctl status rabbitmq-server.service',
        common.UBUNTU: 'service rabbitmq-server status',
    },
}

RABBITMQ = 'RABBITMQ'

common.required_system_packages[RABBITMQ] = {
    common.FEDORA: ['rabbitmq-server'],
    common.UBUNTU: ['rabbitmq-server'],
}

def get_service_command(action):
    os_version = common.get_os_version()
    return env.rabbitmq_service_commands[action][os_version.distro]

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
    if env.rabbitmq_erlang_cookie_template:
        env.rabbitmq_erlang_cookie = env.rabbitmq_erlang_cookie_template % env

@task
def list_vhosts():
    """
    Displays a list of configured RabbitMQ vhosts.
    """
    sudo('rabbitmqctl list_vhosts')

@task
def list_users():
    """
    Displays a list of configured RabbitMQ users.
    """
    sudo('rabbitmqctl list_users')
    
@task
def configure(site=None, full=0, dryrun=0):
    """
    Installs and configures RabbitMQ.
    """
    full = int(full)
    dryrun = int(dryrun)
    
    from burlap import package
#    assert env.rabbitmq_erlang_cookie
    if full:
        package.install_required(type=package.common.SYSTEM, service=RABBITMQ)
    
    #render_paths()
    
    params = set() # [(user,vhost)]
    for site, site_data in common.iter_sites(site=site, renderer=render_paths):
        print '!'*80
        print site
        _settings = common.get_settings(site=site)
        #print '_settings:',_settings
        if not _settings:
            continue
        print 'RabbitMQ:',_settings.BROKER_USER, _settings.BROKER_VHOST
        params.add((_settings.BROKER_USER, _settings.BROKER_VHOST))
    
    for user, vhost in params:
        env.rabbitmq_broker_user = user
        env.rabbitmq_broker_vhost = vhost
        with settings(warn_only=True):
            cmd = 'rabbitmqctl add_vhost %(rabbitmq_broker_vhost)s' % env
            print cmd
            if not dryrun:
                sudo(cmd)
            cmd = 'rabbitmqctl set_permissions -p %(rabbitmq_broker_vhost)s %(rabbitmq_broker_user)s ".*" ".*" ".*"' % env
            print cmd
            if not dryrun:
                sudo(cmd)

def configure_all(**kwargs):
    kwargs['site'] = common.ALL
    return configure(**kwargs)

common.service_configurators[RABBITMQ] = [configure_all]
#common.service_deployers[RABBITMQ] = [deploy]
common.service_restarters[RABBITMQ] = [restart]
