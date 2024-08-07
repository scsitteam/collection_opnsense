.. _modules_routing:

.. include:: ../_include/head.rst

=====
routing
=====

**STATE**: stable

**TESTS**: `Playbook <https://github.com/ansibleguy/collection_opnsense/blob/latest/tests/routing.yml>`_

**API Docs**: `Core - routings <https://docs.opnsense.org/development/api/core/routing.html>`_

**Service Docs**: `routings <https://docs.opnsense.org/manual/gateways.html>`_

Definition
**********

..  csv-table:: Definition
    :header: "Parameter", "Type", "Required", "Default", "Aliases", "Comment"
    :widths: 15 10 10 10 10 45

    "name","string","true","\-","\-","Gateway Name"
    "interface","string","true","\-","nw, net","Interface belonging to this gateway"
    "description","string","false","\-","desc","Optional description for the Gateway. Could be used as unique-identifier when set as only 'match_field'."
    "defaultgw","string","true","\-","\-","This will select the above gateway as a default gateway candidate."
    "fargw","string","false","\-","\-","This will allow the gateway to exist outside of the interface subnet."
    "monitor_disable","boolean","false","false","\-","Disable gateway monitoring"
    "monitor_noroute","boolean","false","false","\-","Do not create a dedicated host route for this monitor."
    "monitor","string","false","\-","\-","IP address to use as a monitor IP for the gateway."
    "force_down","boolean","false","false","\-","Force the gateway to be considered as down."
    "priority","integer","false","255","\-","Choose a value between 1 and 255. Influences sort order when selecting a (default) gateway, lower means more important."
    "weight","integer","false","1","\-","Weight for this gateway when used in a gateway group. Specificed as an integer number between 1 and 5."
    "latencylow","integer","false","200","\-","Latency threshold in milliseconds. If the latency is lower than this value, the gateway is considered as up."
    "latencyhigh","integer","false","500","\-","Latency threshold in milliseconds. If the latency is higher than this value, the gateway is considered as down."
    "losslow","integer","false","10","\-","Packet loss threshold in percent. If the packet loss is lower than this value, the gateway is considered as up."
    "losshigh","integer","false","20","\-","Packet loss threshold in percent. If the packet loss is higher than this value, the gateway is considered as down."
    "interval","integer","false","1","\-","How often that an ICMP probe will be sent in seconds."
    "time_period","integer","false","60","\-","The time period over which results are averaged."
    "loss_interval","integer","false","4","\-","Time interval before packets are treated as lost."
    "data_length","integer","false","0","\-","Size of ICMP packets to send."
    "match_fields","list of strings","false","['name', 'gateway', descriptiom]","\-","Fields that are used to match configured gateways with the running config - if any of those fields are changed, the module will think it's a new gateway"
    "reload","boolean","false","true","\-", .. include:: ../_include/param_reload.rst

.. include:: ../_include/param_basic.rst

Usage
*****

The module somehow needs to link the configured and existing gateays to manage them.

You can to set how this matching is done by setting the 'match_fields' parameter!

The default behaviour is that a routing is matched by its 'name'.


Examples
********

.. code-block:: yaml

    - hosts: localhost
      gather_facts: false
      module_defaults:
        group/ansibleguy.opnsense.all:
          firewall: 'opnsense.template.ansibleguy.net'
          api_credential_file: '/home/guy/.secret/opn.key'

        ansibleguy.opnsense.routing:
          match_fields: ['description']

        ansibleguy.opnsense.list:
          target: 'routing'

      tasks:
        - name: List Gateways
          ansibleguy.opnsense.list:
          register: existing_entries
        - name: Add Gateway
          ansibleguy.opnsense.routing:
            name: 'Test_GW'
            interface: 'wg1'
            gateway: '10.255.255.16'
        - name: Set Gateway Monitor IP
          ansibleguy.opnsense.routing:
            name: 'Test_GW'
            interface: 'wg1'
            gateway: '10.255.255.16'
            monitor: '1.1.1.1'
        - name: Delete Gateway
          ansibleguy.opnsense.routing:
            name: 'Test_GW'
            state: absent
