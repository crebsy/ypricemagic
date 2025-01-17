
import asyncio
import logging
from functools import cached_property
from typing import Any, Optional, Union

import a_sync
from brownie.convert.datatypes import HexString
from brownie.exceptions import ContractNotFound

from y import convert
from y.classes.singleton import ChecksumASyncSingletonMeta
from y.constants import EEE_ADDRESS
from y.contracts import Contract, build_name, has_method, probe
from y.datatypes import AnyAddressType, Block, UsdPrice
from y.erc20 import decimals, totalSupply
from y.exceptions import (ContractNotVerified, MessedUpBrownieContract,
                          NonStandardERC20)
from y.networks import Network
from y.utils.raw_calls import balanceOf

logger = logging.getLogger(__name__)


def hex_to_string(h: HexString) -> str:
    '''returns a string from a HexString'''
    h = h.hex().rstrip("0")
    if len(h) % 2 != 0:
        h += "0"
    return bytes.fromhex(h).decode("utf-8")

class ContractBase(a_sync.ASyncGenericBase, metaclass=ChecksumASyncSingletonMeta):
    def __init__(self, address: AnyAddressType, asynchronous: bool = False) -> None:
        self.address = convert.to_address(address)
        self.asynchronous = asynchronous
        super().__init__()
    
    def __str__(self) -> str:
        return f'{self.address}'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.address}'"
    
    def __eq__(self, __o: object) -> bool:
        try:
            return convert.to_address(__o) == self.address
        except:
            return False
    
    def __hash__(self) -> int:
        return hash(self.address)
    
    @cached_property
    def contract(self) -> Contract:
        return Contract(self.address)
    
    @cached_property
    def _is_cached(self) -> bool:
        try:
            self.contract
            return True
        except (ContractNotVerified):
            return False
        except (ContractNotFound, MessedUpBrownieContract):
            return None

    @a_sync.aka.cached_property
    async def build_name(self) -> str:
        return await build_name(self.address, sync=False)

    async def has_method(self, method: str, return_response: bool = False) -> Union[bool,Any]:
        return await has_method(self.address, method, return_response=return_response, sync=False)


class ERC20(ContractBase):
    def __repr__(self) -> str:
        cls = self.__class__.__name__
        try:
            if ERC20.symbol.has_cache_value(self):
                symbol = ERC20.symbol.get_cache_value(self)
                return f"<{cls} {symbol} '{self.address}'>"
            elif not asyncio.get_event_loop().is_running() and not self.asynchronous:
                return f"<{cls} {self.symbol} '{self.address}'>"
        except AttributeError:
            pass
        return super().__repr__()
    
    @a_sync.aka.cached_property
    async def symbol(self) -> str:
        if self.address == EEE_ADDRESS:
            return "ETH"
        
        symbol = await probe(self.address, ["symbol()(string)", "SYMBOL()(string)", "getSymbol()(string)"])
        if symbol:
            return symbol
        
        # Sometimes the above will fail if the symbol method returns bytes32, as with MKR. Let's try this.
        symbol = await probe(self.address, ["symbol()(bytes32)"])
        if symbol:
            return hex_to_string(symbol)

        # we've failed to fetch
        self.__raise_exception('symbol')
    
    @a_sync.aka.cached_property
    async def name(self) -> str:
        if self.address == EEE_ADDRESS:
            return "Ethereum"
        
        name = await probe(self.address, ["name()(string)", "NAME()(string)", "getName()(string)"])
        if name:
            return name
        
        # Sometimes the above will fail if the name method returns bytes32, as with MKR. Let's try this.
        name = await probe(self.address, ["name()(bytes32)"])
        if name:
            return hex_to_string(name)
                
        # we've failed to fetch
        self.__raise_exception('name')
    
    @a_sync.aka.cached_property
    async def decimals(self) -> int:
        if self.address == EEE_ADDRESS:
            return 18
        return await decimals(self.address, sync=False)

    @a_sync.a_sync # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _decimals(self, block: Optional[Block] = None) -> int:
        '''used to fetch decimals at specific block'''
        if self.address == EEE_ADDRESS:
            return 18
        retval = await decimals(self.address, block=block, sync=False)
        if asyncio.iscoroutine(retval):
            raise Exception(retval)
        return retval
    
    @a_sync.aka.cached_property
    async def scale(self) -> int:
        return 10 ** await self.__decimals__(asynchronous=True)
    
    @a_sync.a_sync # Override the leading underscore so a_sync lib doesn't bypass this fn
    async def _scale(self, block: Optional[Block] = None) -> int:
        return 10 ** await self._decimals(block, sync=False)

    async def total_supply(self, block: Optional[Block] = None) -> int:
        return await totalSupply(self.address, block=block, sync=False)

    async def total_supply_readable(self, block: Optional[Block] = None) -> float:
        total_supply, scale = await asyncio.gather(
            self.total_supply(block=block, sync=False),
            self.__scale__(sync=False)
        )
        return total_supply / scale
    
    async def balance_of(self, address: AnyAddressType, block: Optional[Block] = None) -> int:
        return await balanceOf(self.address, address, block=block, sync=False)
    
    async def balance_of_readable(self, address: AnyAddressType, block: Optional[Block] = None) -> float:
        balance, scale = await asyncio.gather(self.balance_of(address, block=block, asynchronous=True), self.__scale__(asynchronous=True))
        return balance / scale

    async def price(self, block: Optional[Block] = None, return_None_on_failure: bool = False) -> Optional[UsdPrice]:
        from y.prices.magic import get_price
        return await get_price(
            self.address, 
            block=block, 
            fail_to_None=return_None_on_failure,
            sync=False,
        )
    
    def __raise_exception(self, fn_name: str):
        raise NonStandardERC20(f'''
            Unable to fetch `{fn_name}` for {self.address} on {Network.printable()}
            If the contract is verified, please check to see if it has a strangely named
            `{fn_name}` method and create an issue on https://github.com/BobTheBuidler/ypricemagic
            with the contract address and correct method name so we can keep things going smoothly :)''')


class WeiBalance(a_sync.ASyncGenericBase):
    def __init__(
        self, balance: int,
        token: AnyAddressType,
        block: Optional[Block] = None,
        asynchronous: bool = False,
        ) -> None:

        self.asynchronous = asynchronous
        self.balance = balance
        self.token = ERC20(str(token), asynchronous=self.asynchronous)
        self.block = block
        super().__init__()

    def __str__(self) -> str:
        return str(self.balance)

    def __eq__(self, __o: object) -> bool:
        return __o == self.balance
    
    @a_sync.aka.property
    async def readable(self) -> float:
        if self.balance == 0:
            return 0
        return self.balance / await self.token.__scale__(sync=False)
    
    @a_sync.aka.property
    async def value_usd(self) -> float:
        if self.balance == 0:
            return 0
        balance, price = await asyncio.gather(
            self.__readable__(sync=False),
            self.token.price(block=self.block, sync=False),
        )
        return balance * price
