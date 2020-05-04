#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Anthony Winters <info@nforce-it.nl>

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ldap_search

short_description: Retrieve attributes of userObject in ActiveDirectory.

version_added: "2.9"

description:
    - "This module can lookup a user in Active Directory and retrieve the userObject attributes"

options:
    username:
        description:
            - This is the username of the Active Directory user.
        required: true
    ldap_host:
        description:
            - This is the domain controller or domain name suffix of the Active Directory Domain.
        required: true
    ldap_base:
        description:
            - This is the base of the Active Directory Domain where we search for the user.      
        required: true  
    ldap_user:
        description:
            - This is the user to authenticate with the Active Directory Domain.
        required: true        
    ldap_password:
        description:
            - This is the password of the user to authenticate with the Active Directory Domain.
        required: true
    ldap_port:
        description:
            - The port to use to connect with the Active Directory Domain.
        default: 389             

extends_documentation_fragment:
    - ldap_search

author:
    - A.R. Winters <info@nforce-it.nl>
'''

EXAMPLE = '''
# Lookup user and retrieve attributes
- ldap_search:
    ldap_host: nforce-it.nl
    ldap_user: administrator@nforce-it.nl
    ldap_password: password
    ldap_base: dc=nforce-it, dc=nl
    username: tony
'''

RETURN = '''
{
  "changed": false,
  "company": "NForce IT",
  "display_name": "Tony Montana",
  "firstname": "Tony",
  "invocation": {
    "module_args": {
      "ldap_base": "dc=nforce-it, dc=nl",
      "ldap_host": "nforce-it.nl",
      "ldap_password": "password",
      "ldap_port": "389",
      "ldap_user": "administrator@nforce-it.nl",
      "username": "tony"
    }
  },
  "lastname": "Montana",
  "mail": "tony.montana@nforce-it.nl",
  "sam_account_name": "Tony"
}
'''

from ansible.module_utils.basic import AnsibleModule
import ldap


def _disconnect(session):
    disconnect = session.unbind_s()
    return disconnect


def _connect(module):
    ldap_server = module.params['ldap_host'] + ":" + module.params['ldap_port']

    try:
        session = ldap.initialize("ldap://{}".format(ldap_server))
        session.protocol_version = ldap.VERSION3
        session.set_option(ldap.OPT_REFERRALS, 0)
        session.simple_bind_s(module.params['ldap_user'], module.params['ldap_password'])
    except ldap.INVALID_CREDENTIALS:
        module.fail_json(msg="Invalid Credentials")
    except ldap.LDAPError as e:
        module.fail_json(exception=e, msg=e.message)

    return session


def _search_user(module):

    session = _connect(module)

    try:
        base = module.params['ldap_base']
        search_filter = "(&(objectClass=user)(sAMAccountName={}))".format(module.params['username'])
        query = session.search_s(base, ldap.SCOPE_SUBTREE, search_filter)
        results = [entry for dn, entry in query if isinstance(entry, dict)]

        result = {
            "firstname": results[0]['name'][0],
            "lastname": results[0]['sn'][0],
            "display_name": results[0]['displayName'][0],
            "mail": results[0]['mail'][0],
            "company": results[0]['company'][0],
            "sam_account_name": results[0]['sAMAccountName'][0],
        }

        module.exit_json(**result)
    except ldap.LDAPError as e:
        module.fail_json(changed=False,
                         exception=e,
                         msg="Failed to read attributes for user --> {}".format(module.params['username']))
    finally:
        _disconnect(session)


def main():
    module_args = dict(
        ldap_host=dict(type="str", required=True),
        ldap_user=dict(type="str", required=True),
        ldap_base=dict(type="str", required=True),
        ldap_password=dict(type="str", required=True),
        ldap_port=dict(type="str", required=False, default="389"),
        username=dict(type="str", required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )

    _search_user(module)


if __name__ == '__main__':
    main()
