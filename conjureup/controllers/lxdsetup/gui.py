import ipaddress

from conjureup.app_config import app
from conjureup.ui.views.lxdsetup import LXDSetupView

from . import common


class LXDSetupController(common.BaseLXDSetupController):
    async def get_lxd_devices(self):
        devices = {
            'networks': await app.provider.get_networks(),
            'storage-pools': await app.provider.get_storage_pools()
        }

        self.view = LXDSetupView(devices, self.finish)
        self.view.show()

    async def set_lxd_info(self, data):
        net_info = await app.provider.get_network_info(data['network'])
        app.log.debug(net_info)
        if net_info:
            self.set_state('lxd-network-name', net_info['name'])
            if net_info['config']:
                iface = ipaddress.IPv4Interface(
                    net_info['config']['ipv4.address'])
                self.set_state('lxd-network', iface.network)
                self.set_state('lxd-gateway', iface.ip)
                self.set_state('lxd-network-dhcp-range-start',
                               iface.ip + 1)
                # To account for current interface taking 1 ip
                number_of_hosts = len(list(iface.network.hosts())) - 1
                self.set_state('lxd-network-dhcp-range-stop',
                               "{}".format(iface.ip + number_of_hosts))
        self.set_state('lxd-storage-pool', data['storage-pool'])
        app.log.debug('LXD Info set: (network: {}) '
                      '(gateway: {}) '
                      '(dhcp-range-start: {}) '
                      '(dhcp-range-stop: {})'.format(
                          self.get_state('lxd-network'),
                          self.get_state('lxd-gateway'),
                          self.get_state('lxd-network-dhcp-range-start'),
                          self.get_state('lxd-network-dhcp-range-stop')))

    def finish(self, data):
        app.loop.create_task(self.set_lxd_info(data))
        return self.next_screen()

    def render(self):
        app.loop.create_task(self.get_lxd_devices())


_controller_class = LXDSetupController
