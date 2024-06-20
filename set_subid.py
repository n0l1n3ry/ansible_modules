# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Bruno FABRE <bruno.fabre@protonmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: set_subid

short_description: Permet la création d'une entrée utilisateur ou groupe dans les fichiers /etc/subuid et /etc/subgid.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Permet la création d'une entrée utilisateur ou groupe dans les fichiers /etc/subuid et /etc/subgid.

options:
    user:
        description: Le nom ou l'ID de l'utilisateur à rajouter dans le fichier /etc/subuid.
        required: false
        type: str
    group:
        description: Le nom ou l'ID du groupe à rajouter dans le fichier /etc/subgid.
        required: false
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Bruno FABRE (@n0l1n3ry)
'''

EXAMPLES = r'''
# Ajout de l'utilisateur et du groupe toto aux fichiers /etc/sub(uid|gid)
- name: Add toto user & group to the /etc/subuid and /etc/subgid files
  my_namespace.my_collection.set_uid_gid: # Specify this value according to your collection
    user: toto
    group: toto
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
message:
    description: Le message d'output généré par le module lui-même.
    type: str
    returned: always
    sample: 'User toto added'
'''


from ansible.module_utils.basic import AnsibleModule
import re

def search_uidgid(file, search_string):
    with open(file, 'r') as file:
        file_contents = file.read()
        resultat = re.search(search_string, file_contents)
        file.close()
        if resultat:
            return resultat.group(0)

def add_uid_gid(file, sub_id):
    with open(file, "r+") as f:
        last_line = f.readlines()[-1]
        last_uid = last_line.split(":")[1]
        f.write("%s:%d:%d\n" %(sub_id,int(last_uid)+65536,65536))
        f.close()


def main():
    module = AnsibleModule(
        argument_spec=dict(
        user   = dict(required=False, type='str'),
        group  = dict(required=False, type='str')
        ),
        supports_check_mode=True
    )

    user_local = module.params.get('user')
    group_local = module.params.get('group')
    result = dict(
        changed=False,
        message=[]
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        if module.params['user']:
            user_match = search_uidgid("/etc/subuid", user_local)
            if user_match != user_local:
                result['message'] += [ "User %s added" %(user_local) ]
                result['changed'] = True

        if module.params['group']:
            group_match = search_uidgid("/etc/subgid", group_local)
            if group_match != group_local:
                result['message'] += [ "Group %s added" %(group_local) ]
                result['changed'] = True

        module.exit_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    if module.params['user']:
        user_match = search_uidgid("/etc/subuid", user_local)
        if user_match != user_local:
            add_uid_gid("/etc/subuid", user_local)
            result['message'] += [ "User %s added" %(user_local) ]
            result['changed'] = True

    if module.params['group']:
        group_match = search_uidgid("/etc/subgid", group_local)
        if group_match != group_local:
            add_uid_gid("/etc/subgid", group_local)
            result['message'] += [ "Group %s added" %(group_local) ]
            result['changed'] = True

    module.exit_json(**result)

if __name__ == "__main__":
    main()

