import logging

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from web3 import Web3

from hexbytes import HexBytes
from eth_account.datastructures import SignedTransaction


class TransactionError(Exception): 
    pass


class TransactionHandler:
    def __init__(self, w3: "Web3", chain_id: int, defaults: dict):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.w3 = w3
        self.chain_id = chain_id
        self.defaults = defaults
        self.owner: Optional[str] = None
        self.private_key: Optional[HexBytes] = None
        
    def transact(self, func: callable, args: tuple, timeout: Optional[int] = None):
        """ Submits transaction and prints hash """
        if not self.private_key:
            raise TransactionError("Private key not set")
        if not timeout:
            timeout = self.defaults.get("timeout")
        stxn = self._build_signed_txn(func, args)
        sent = self.w3.eth.send_raw_transaction(stxn.rawTransaction)
        rcpt = self.w3.eth.wait_for_transaction_receipt(sent, timeout=timeout)
        self.logger.info(f"Block Hash: {rcpt.blockHash.hex()}")
        self.logger.info(f"Gas Used: {rcpt.gasUsed}")
        if rcpt["status"] != 1:
            raise TransactionError(f"Transaction status is not 1 ({rcpt['status']})")
        return sent, rcpt
    
    def _build_signed_txn(self, func: callable, args: tuple) -> SignedTransaction:
        call = func(*args)
        details = self._txn_details(call)
        txn = call.buildTransaction(details)
        return self.w3.eth.account.sign_transaction(txn, private_key=self.private_key)

    def _txn_details(self, call: callable):
        return {
            "chainId" : self.chain_id,
            "gas" : self.gas(call),
            "gasPrice" : self.gas_price(),
            "nonce" : self.w3.eth.getTransactionCount(self.owner),
        }

    def gas(self, call: callable) -> int:
        if self.defaults.get('gas.useEstimate'):
            return self._estimate_call_gas(call)
        return self.defaults.get('gas.exact')
    
    def _estimate_call_gas(self, call: callable) -> int:
        return int(call.estimateGas())

    def gas_price(self):
        return self.w3.toWei(
            self.defaults.get('gasPrice.number'), 
            self.defaults.get('gasPrice.unit')
        )
