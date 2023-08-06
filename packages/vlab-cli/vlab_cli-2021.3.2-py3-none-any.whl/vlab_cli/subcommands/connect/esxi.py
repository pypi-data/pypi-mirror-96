# -*- coding: UTF-8 -*-
"""Defines the CLI for connecting to an ESXi instances"""
import getpass

import click

from vlab_cli.lib.widgets import Spinner
from vlab_cli.lib.api import consume_task
from vlab_cli.lib.connectorizer import Connectorizer
from vlab_cli.lib.click_extras import MandatoryOption
from vlab_cli.lib.portmap_helpers import get_protocol_port


@click.command()
@click.option('-p', '--protocol', type=click.Choice(['ssh', 'scp', 'https', 'console'], case_sensitive=False),
              default='https', show_default=True,
              help='The protocol to connect with')
@click.option('-n', '--name', cls=MandatoryOption,
              help='The name of the ESXi instance to connect to')
@click.option('-u', '--user', default='root',
              help='The name of the user to connect to the ESXi instance as.')
@click.option('--password', default=False, is_flag=True,
              help='If supported, auto-enter the password when connecting.')
@click.pass_context
def esxi(ctx, name, protocol, user, password):
    """Connect to an ESXi instances"""
    if protocol == 'console':
        info = consume_task(ctx.obj.vlab_api,
                            endpoint='/api/2/inf/esxi',
                            message='Looking up connection info for {}'.format(name),
                            method='GET').json()
        if not info['content'].get(name, None):
            error = 'No ESXi VM named {} found'.format(name)
            raise click.ClickException(error)
        else:
            vm_moid = info['content'][name].get('moid', 'n/a')
        conn = Connectorizer(ctx.obj.vlab_config, gateway_ip='n/a')
        conn.console(vm_moid)
    else:
        target_port = get_protocol_port('ecs', protocol)
        with Spinner('Lookin up connection information for {}'.format(name)):
            resp = ctx.obj.vlab_api.get('/api/1/ipam/portmap', params={'name' : name, 'target_port' : target_port}).json()
            try:
                conn_port = list(resp['content']['ports'].keys())[0]
            except Exception as doh:
                ctx.obj.log.debug(doh, exc_info=True)
                conn_port = None
        if not conn_port:
            error = 'No mapping rule for {} to {} exists'.format(protocol, name)
            raise click.ClickException(error)

        if password:
            password_value = getpass.getpass('Password for {}: '.format(user))
            conn = Connectorizer(ctx.obj.vlab_config, resp['content']['gateway_ip'], user=user, password=password_value)
        else:
            conn = Connectorizer(ctx.obj.vlab_config, resp['content']['gateway_ip'], user=user)
        if protocol == 'ssh':
            conn.ssh(port=conn_port)
        elif protocol == 'https':
            conn.https(port=conn_port)
        elif protocol == 'scp':
            conn.scp(port=conn_port)
        else:
            error = 'Unexpected protocol requested: {}'.format(protocol)
            raise RuntimeError(error)
