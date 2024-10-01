.. _modules_category:

.. include:: ../_include/head.rst

============
MODULE TITLE
============

**STATE**: unstable

**TESTS**: `Playbook <https://github.com/ansibleguy/collection_opnsense/blob/latest/tests/category.yml>`_

**API Docs**: `category <https://docs.opnsense.org/development/api/core/firewall.html>`_

**Service Docs**: `category <https://docs.opnsense.org/manual/firewall_categories.html>`_


Definition
**********

..  csv-table:: Definition
    :header: "Parameter", "Type", "Required", "Default", "Aliases", "Comment"
    :widths: 15 10 10 10 10 45

    "name","str","true","\-","\-","Name for this category"
    "color","string","false","\-","\-","Color for this category"
    "auto","bool","false","\-","\-","Mark as automatically added."

.. include:: ../_include/param_basic.rst

Usage
*****

Manages firewall categories in OPNsense.

Categories can be used to ease the maintenance of larger rulesets by categorising rules, aliases, etc.

Examples
********

.. code-block:: yaml

    - hosts: localhost
      gather_facts: false
      module_defaults:
        group/ansibleguy.opnsense.all:
          firewall: 'opnsense.template.ansibleguy.net'
          api_credential_file: '/home/guy/.secret/opn.key'

        ansibleguy.opnsense.list:
          target: 'category'

      tasks:
        # add optional parameters commented-out
        # required ones normally
        # add their default values to get a brief overview of how the module works
        - name: Example
          ansibleguy.opnsense.category:
            name: 'Ansible Managed'
            color: 'ff0000'
            # auto: false
            # state: 'absent'
            # debug: false

        - name: Adding Ansible Managed Category
          ansibleguy.opnsense.category:
            name: 'Ansible Managed'
            color: 'ff0000'

        - name: Updating color
          ansibleguy.opnsense.category:
            name: 'Ansible Managed'
            color: '008000'

        - name: Listing categories
          ansibleguy.opnsense.list:
          #  target: 'category'
          register: existing_categories

        - name: Printing
          ansible.builtin.debug:
            var: existing_categories.data
