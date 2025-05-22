class VirtualServerManager:
    def __init__(self, config):
        self.servers = {}
        for server_config in config['server']:
            port = server_config['port']
            if port not in self.servers:
                self.servers[port] = []
            self.servers[port].append(server_config)
    
    
    def find_server(self, port: int, server_name: str):
        if port not in self.servers:
            return None
        
        for server in self.server[port]:
            if server.get("server_name") == server_name:
                return server
            
        return self.servers[port][0] if self.servers[port] else None