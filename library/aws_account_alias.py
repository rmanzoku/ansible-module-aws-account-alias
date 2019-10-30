#!/usr/bin/python

# Copyright: (c) 2019, Ryo Manzoku (@rmanzoku)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass

def _get_account_alias(client, params, module):
    alias = client.list_account_aliases()
    if len(alias.get("AccountAliases")) == 0:
        return ""
    return alias.get("AccountAliases")[0]

def create_account_alias(client, params, module):
    alias = params.get("name")
    try:
        client.create_account_alias(
            AccountAlias=alias,
        )
    except (BotoCoreError, ClientError) as e:
        raise e

    return True


def delete_account_alias(client, params, module, current):
    try:
        client.delete_account_alias(
            AccountAlias=current,
        )
    except (BotoCoreError, ClientError) as e:
        raise e

    return True


def main():

    argument_spec = (
        dict(
            state=dict(require=False, type='str', default='present',
                       choices=['present', 'absent']),
            name=dict(required=False, type='str',
                      aliases=['alias']),
        )
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['name']),
        ]
    )

    client = module.client('iam')
    params = module.params

    current = _get_account_alias(client, params, module)
    print(current)

    changed = False
    if params.get('state') == 'present':
        if current != params.get("name"):
            changed = create_account_alias(client, params, module)
    else:
        if current != "":
            changed = delete_account_alias(client, params, module, current)

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
