class VirtualServerManager:
    def __init__(self, config):
        self.servers = []
        for server_config in config["server"]:
            self.servers.append(server_config)

    def find_server(self, server_name: str) -> dict:
        for server in self.servers:
            if server.get("server_name") == server_name:
                return server
