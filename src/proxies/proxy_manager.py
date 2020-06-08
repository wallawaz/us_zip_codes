from proxyscrape import (
   add_resource_type,
   create_collector,
   get_proxyscrape_resource,
)

#
#class ProxyManager:
#    def __init__(self, proxytype, timeout=5000, ssl='yes', anonymity='anonymous', country='us'):
#        self.resource_name = get_proxyscrape_resource(
#            proxytype=proxytype,
#            timeout=timeout,
#            ssl=ssl,
#            anonymity=anonymity,
#            country=country,
#        )
#        add_resource_type(self.resource_name)
#        self.collector = create_collector("custom_collector_{proxytype}", self.resource_name)
#        self.proxy_map = dict()
#
#    def get_proxy(self):
#        return self.collector.get_proxy()
#
collector = create_collector('custom_collector', ['socks5']) 