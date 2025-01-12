from loader import ConfigLoader
import abc

class Server(metaclass=abc.ABCMeta):
    def __init__(self, name:str, nickname:str, serialnum:str, device_addr:int, connected_client):
        self.name: str = name
        self.nickname: str = nickname
        self.serialnum: str = serialnum
        self.connected_client = connected_client
        self.registers: list = []
        self.manufacturer:str | None = None
        self.model:str | None = None
        self.device_addr:int| None = None
        # self.batches TODO

    def verify_serialnum(self, serialnum_name_in_definition:str="Serial Number"):
        """ Verify that the serialnum specified in config.yaml matches 
        with the num in the regsiter as defined in implementation of Server

        Arguments:
        ----------
            - serialnum_name_in_definition: str: Name of the register in server.registers containing the serial number
        """
        serialnum = server.connected_client.read_registers(server, serialnum_name_in_definition, 
                                                            server.registers[serialnum_name_in_definition])

        if self.serialnum is None: raise ConnectionError(f"Failed to read serialnum of {self.nickname}.")
        elif self.serialnum != serialnum_as_read: raise ValueError(f"Mismatch in configured serialnum {self.serialnum} \
                                                                        and actual serialnum {serialnum_as_read} for server {self.nickname}.")

    def from_config(server_cfg:dict, clients:list):
        # assume valid configLoader object
        try:
            idx = [str(client) for c in clients].index(server_cfg["connected_client"])  # TODO ugly
        except:
            raise ValueError(f"Client {server_cfg['connected_client']} from server {server_cfg['nickname']} config not defined in client list")

        return Server(server_cfg["name"], server_cfg["nickname"], server_cfg["serialnum"], server_cfg['device_addr'], connected_client=clients[idx])

    @abc.abstractmethod
    def _decoded(content):
        "Server-specific decoding must be implemented."
        pass

    @abc.abstractmethod
    def _encoded(content):
        "Server-specific encoding must be implemented."
        pass
