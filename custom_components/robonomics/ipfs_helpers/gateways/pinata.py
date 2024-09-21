from .gateway import Gateway, PinArgs, UnpinArgs
from homeassistant.core import HomeAssistant
from pinatapy import PinataPy
import typing as tp
import logging
from ...const import PINATA_GATEWAY, DOMAIN

_LOGGER = logging.getLogger(__name__)

class Pinata(Gateway):

    def __init__(self, hass: HomeAssistant, pinata_pub: str, pinata_secret: str, websession) -> None:
        self.pinata_py = PinataPy(pinata_pub, pinata_secret)
        self.hass = hass
        super().__init__(self.hass, self.hass.data[DOMAIN][PINATA_GATEWAY], websession)
    
    async def pin(self, args: PinArgs) -> str:
        file_name: str = args.file_name
        _LOGGER.debug(f"Start adding {file_name} to Pinata")
        try:
            res = None
            res = self.hass.async_add_executor_job(self._pin_to_pinata, file_name)
            ipfs_hash: tp.Optional[str] = res["IpfsHash"]
            _LOGGER.debug(f"File {file_name} was added to Pinata with cid: {ipfs_hash}")
        except Exception as e:
            _LOGGER.error(f"Exception in pinata pin: {e}, pinata response: {res}")
            ipfs_hash = None
            return ipfs_hash
        return ipfs_hash
    
    def _pin_to_pinata(self, file_name: str):
        return self.pinata_py.pin_file_to_ipfs(file_name, save_absolute_paths=False)
    
    async def unpin(self, args: UnpinArgs) -> None:
        last_file_hash: str = args.last_file_hash
        try:
            self.hass.async_add_executor_job(self._unpin_from_pinata, last_file_hash)
        except Exception as e:
            _LOGGER.warning(f"Exception in unpinning file from Pinata: {e}")
    
    def _unpin_from_pinata(self, last_file_hash: str) -> None:
        self.pinata_py.remove_pin_from_ipfs(last_file_hash)
    

        

