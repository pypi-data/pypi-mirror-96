import argparse
import json
import os

from network_runner import api
from network_runner.models.inventory import Inventory

TRUNK_SUPPORT = ('cumulus', 'eos', 'junos', 'openvswitch')
STP_EDGE_SUPPORT = ('nxos')
PORTS = {
    'cumulus': 'swp1',
    'eos': 'Ethernet1',
    'nxos': 'Eth1/1',
    'junos': 'xe-0/0/1',
    'openvswitch': 'testport',
    }
PORTS2 = {
    'nxos': 'Eth1/2',
}

HOSTNAME = 'eos-4.20.10'
HOSTNAME = 'appliance'
VLAN = 37
T_VLANS = [3, 7, 73]
INVENTORY_FILE = os.getenv('ANSIBLE_INVENTORY_FILE', '/etc/ansible/hosts')


def get_parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', help='hosts file',
                        default=INVENTORY_FILE)
    return parser.parse_args()


def get_inv_yaml(args):
    f = open(args.hosts)

    # ## Parses Ansible hosts file format
    # https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/inventory
    # lines = f.readlines()
    # hosts = {}
    # for l in lines:
    #     print(l)
    #     line = l.split(' ')
    #     if l[0] != '#' and ' ' in l:
    #         hosts[line[0]] = {
    #             k: val for (k, val) in [x.split('=') for x in line[1:]]
    #         }
    # return {'all': {'hosts': hosts}}

    json_hosts = f.read()
    hosts = json.loads(json_hosts)
    return hosts


def run_tests(inventory, hostname, port, trunk=False, edge=False):
    # TODO(radez) Use a testing framework to verify

    net_runr = api.NetworkRunner(inventory)
    # ## Create a vlan
    net_runr.create_vlan(hostname, VLAN)

    # ## Configure an access port
    net_runr.conf_access_port(hostname, port, VLAN)

    # ## configure a trunk port
    if trunk:
        net_runr.conf_trunk_port(hostname, port, VLAN, T_VLANS)

    if edge:
        # ## Configure an access port
        net_runr.conf_access_port(hostname, port, VLAN, edge=edge)

        # ## configure a trunk port
        if trunk:
            net_runr.conf_trunk_port(hostname, port, VLAN, T_VLANS, edge=edge)

    # ## delete a port
    net_runr.delete_port(hostname, port)
    # ## delete a vlan
    net_runr.delete_vlan(hostname, VLAN)


def main():
    # collect information for the run.
    args = get_parser_args()
    inv_yaml = get_inv_yaml(args)
    hosts = inv_yaml['all']['hosts']
    hostname = inv_yaml['all']['children'][HOSTNAME]['hosts'].popitem()[0]
    net_os = hosts[hostname]['ansible_network_os']
    port = PORTS[net_os]

    # build the inventory object
    inventory = Inventory()
    inventory.deserialize(inv_yaml)

    # execute the tests
    run_tests(inventory, hostname, port,
              net_os in TRUNK_SUPPORT,
              net_os in STP_EDGE_SUPPORT)


if __name__ == "__main__":
    main()
