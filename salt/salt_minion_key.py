#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Anthony Winters <info@nforce-it.nl>


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: salt_minion_key

short_description: This module can manage a Salt Minion key.

version_added: "2.9"

description:
    - "This module can manage a Salt Minion key. Like: Accept, Reject or Delete"

options:
    hostname:
        description:
            - This is the hostname of salt-minion
        required: true
    state:
        description:
            - Choose present, absent or disable 
        required: true
    config:
        description:
            - Salt master location of configuration file
        required: false
        default: /etc/salt/master

extends_documentation_fragment:
    - salt_minion_key

author:
    - A.R. Winters <info@nforce-it.nl>
'''

EXAMPLE = '''
# Accept Salt Minion Key
-  salt_minion_key:
     hostname: minion1
     state: present
   delegate_to: saltmaster
   become: true

# Reject Salt Minion Key
-  salt_minion_key:
     hostname: minion1
     state: disable
   delegate_to: saltmaster
   become: true

# Remove Salt Minion Key
-  salt_minion_key:
     hostname: minion1
     state: absent
   delegate_to: saltmaster
   become: true
'''

RETURN = '''
{
  "ansible_facts": {
    "discovered_interpreter_python": "/usr/bin/python"
  },
  "changed": "true",
  "hostname": "minion1.local",
  "invocation": {
    "module_args": {
      "config": "/etc/salt/master",
      "hostname": "minion1.local",
      "state": "[present]"
    }
  },
  "salt_event": {
    "jid": "20200501231538136283",
    "tag": "salt/wheel/20200501231538136283"
  },
  "state": "present"
}
'''

from ansible.module_utils.basic import AnsibleModule
import salt.config
import salt.wheel


def _set_options(module):
    opts = salt.config.master_config(module.params['config'])
    wheel = salt.wheel.WheelClient(opts)
    return wheel


def _reject_key(module):
    salt_command = _set_options(module)

    try:
        reject_key_result = salt_command.cmd_async({'fun': 'key.reject',
                                                    'match': module.params['hostname'],
                                                    'include_accepted': 'True',
                                                    'include_denied': 'True'})
    except salt.exceptions.SaltWheelError as e:
        module.fail_json(changed=False, exception=e)

    results = {
      "hostname": module.params['hostname'],
      "state": module.params['state'],
      "changed": "true",
      "salt_event": reject_key_result
    }
    module.exit_json(**results)


def _accept_key(module):
    salt_command = _set_options(module)

    try:
        accept_key_result = salt_command.cmd_async({'fun': 'key.accept',
                                                    'match': module.params['hostname'],
                                                    'include_rejected': 'True',
                                                    'include_denied': 'True'})
    except salt.exceptions.SaltWheelError as e:
        module.fail_json(changed=False, exception=e)

    results = {
      "hostname": module.params['hostname'],
      "state": module.params['state'],
      "changed": "true",
      "salt_event": accept_key_result
    }
    module.exit_json(**results)


def _delete_key(module):
    salt_command = _set_options(module)

    try:
        delete_key_result = salt_command.cmd_async({'fun': 'key.delete',
                                                    'match': module.params['hostname']})
    except salt.exceptions.SaltWheelError as e:
        module.fail_json(changed=False, exception=e)

    results = {
      "hostname": module.params['hostname'],
      "state": module.params['state'],
      "changed": "true",
      "salt_event": delete_key_result
    }
    module.exit_json(**results)


def main():
    module_args = dict(
        hostname=dict(type="str", required=True),
        state=dict(
          type="str",
          required=True,
          choices=["absent", "present", "disable"],
        ),
        config=dict(
          type="str",
          default="/etc/salt/master"
        )
      )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )

    state = module.params["state"]
    if state == "present":
        _accept_key(module)
    elif state == "absent":
        _delete_key(module)
    elif state == "disable":
        _reject_key(module)


if __name__ == '__main__':
    main()
