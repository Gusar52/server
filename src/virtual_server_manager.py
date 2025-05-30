from typing import Dict, List, Optional, Any

class VirtualServerManager:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.servers: List[Dict[str, Any]] = []
        for server_config in config["server"]:
            self.servers.append(server_config)

    def find_server(self, server_name: str) -> Optional[Dict[str, Any]]:
        for server in self.servers:
            if server.get("server_name") == server_name:
                return server
        return None
