# -*- coding: UTF-8 -*-
"""Help users with the ``vlab connect`` command"""
import os
import platform

import click

from vlab_cli.lib import configurizer
from vlab_cli.lib.clippy.utils import prompt_and_confirm
from vlab_cli.lib.widgets import typewriter, prompt, Spinner


def invoke_bad_missing_config(username, vlab_url):
    """Helps a user fix their vlab.ini config file"""
    typewriter("Hi {}, looks like your vLab configuration file has a problem.".format(username))
    typewriter("The file is located at {}".format(configurizer.CONFIG_FILE))
    typewriter("In order to use the 'vlab connect' commands, we'll have to fix it.")
    typewriter("\nYou can manually fix that file by referencing the spec")
    typewriter("in the official documentation located at: {}".format(vlab_url))
    typewriter("Or I can attempt to fix the file right now (by asking you a pile of questions).")
    return prompt("Do you want me to try and fix your config file? [Yes/no]", boolean=True, boolean_default=True)

def invoke_config():
    """Initial config setup help"""
    the_os = platform.system().lower()
    typewriter("In order for 'vlab connect' to work, you'll need to have a")
    typewriter("browser, an SSH client, an SCP client and the VMware Remote Client (VMRC) installed.")
    typewriter("Based on your OS, I can use the following:")
    typewriter(", ".join(configurizer.SUPPORTED_PROGS))
    if the_os == 'windows':
        typewriter("\nNote: 'wt' is short for Windows Terminal, which also requires 'ssh' to be installed.")
        typewriter("Note: mstsc is the default RDP client that comes with Windows")

    typewriter('\nIf you do not have the SSH, RDP, SCP and VMRC clients as well as a supported browser')
    typewriter("installed you'll be wasting time by continuing with this config setup.")
    keep_going = prompt("Continue with config setup? [Yes/no]", boolean=True, boolean_default=True)
    if not keep_going:
        raise RuntimeError("vlab connect prerequisites not met")
    with Spinner('Great! Give me a couple of minutes to find those programs'):
        found_programs = configurizer.find_programs()
        firefox = found_programs.get('firefox', '')
        chrome = found_programs.get('chrome', '')
        putty = found_programs.get('putty', '')
        secure_crt = found_programs.get('securecrt', '').lower()
        windows_term = found_programs.get('wt', '')
        winscp = found_programs.get('winscp', '').lower()
        filezilla = found_programs.get('filezilla', '')
        scp = found_programs.get('scp', '')

    browsers = [x for x in [firefox, chrome] if x]
    if firefox and chrome:
        forget_browsers = which_client(browsers, 'Browser')
        for browser in forget_browsers:
            found_programs.pop(browser)

    scp_clients = [x for x in [winscp, filezilla, scp] if x]
    if len(scp_clients) > 1:
        forget_scp = which_client(scp_clients, 'SCP')
        for scp_client in forget_scp:
            found_programs.pop(scp_client)

    ssh_clients = [x for x in [putty, secure_crt, windows_term] if x]
    if len(ssh_clients) > 1:
        forget_ssh_clients = which_client(ssh_clients, 'SSH')
        for ssh_client in forget_ssh_clients:
            found_programs.pop(ssh_client)

    if len(found_programs) != 5:
        # They are missing some dependency...
        if the_os == 'windows':
            scanned_drive = 'C:\\'
        else:
            scanned_drive = '/ (i.e. root)'
        typewriter("\nUh oh, there's a problem. I wasn't able to find everything under {}.".format(scanned_drive))
        typewriter("Here are the programs I was able to locate:\n\t{}".format(' '.join(found_programs.keys())))
        typewriter("Please install the missing software, then re-run the 'vlab init' command.")
        raise click.ClickException('Missing required dependencies')
    return _make_config(found_programs)


def _make_config(found_programs):
    """Create the config file data structure

    :Returns: Dictionary

    :param found_programs: The result of walking the user's filesystem
    :type found_programs: Dictionary
    """
    new_config = {}
    for agent, prog_path in found_programs.items():
        if agent.lower() in ('putty', 'gnome-terminal', 'securecrt', 'wt'):
            new_config['SSH'] = {'agent': agent, 'location': prog_path}
        elif agent in ('firefox', 'chrome'):
            new_config['BROWSER'] = {'agent' : agent, 'location': prog_path}
        elif agent.lower() in ('scp', 'winscp', 'filezilla'):
            new_config['SCP'] = {'agent': agent, 'location': prog_path}
        elif agent.lower() in ('mstsc', 'remmina'):
            new_config['RDP'] = {'agent': agent, 'location': prog_path}
        elif agent.lower() == 'vmrc':
            new_config['CONSOLE'] = {'agent': agent, 'location': prog_path}
        else:
            raise RuntimeError('Unexpected value for config: {} and {}'.format(agent, prog_path))
    return new_config


def which_client(clients, kind):
    """If a user has multiple SSH clients, prompt them about which one to use"""
    typewriter('Looks like you have several {} clients installed installed.'.format(kind))
    choices = [os.path.splitext(os.path.basename(x))[0] for x in clients]
    choice_question = "Which do you prefer? [{}]".format('/'.join([x.title() for x in choices]))
    confirm_question = "Ok, use {}? [yes/No]"
    answer = prompt_and_confirm(choice_question, confirm_question).lower()
    while answer not in choices:
        typewriter('Invalid choice: {}'.format(answer))
        answer = prompt_and_confirm(choice_question, confirm_question).lower()
    losers = [x for x in choices if not x.startswith(answer)]
    return losers
