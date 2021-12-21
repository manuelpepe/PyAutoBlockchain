import logging

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from web3 import Web3
    from web3.types import TxReceipt

from eth_account.datastructures import SignedTransaction
from eth_account.account import Account

from pab.config import Config


class TransactionError(Exception): 
    pass


class TransactionHandler:
    def __init__(self, w3: "Web3", chain_id: int, config: Config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.w3 = w3
        self.chain_id = chain_id
        self.config = config
        
    def transact(self, account: Account, func: callable, args: tuple, timeout: Optional[int] = None) -> "TxReceipt":
        """ Submits transaction and prints hash """
        if not timeout:
            timeout = self.config.get("transactions.timeout")
        stxn = self._build_signed_txn(account, func, args)
        sent = self.w3.eth.send_raw_transaction(stxn.rawTransaction)
        rcpt = self.w3.eth.wait_for_transaction_receipt(sent, timeout=timeout)
        self.logger.info(f"Block Hash: {rcpt.blockHash.hex()}")
        self.logger.info(f"Gas Used: {rcpt.gasUsed}")
        return rcpt
    
    def _build_signed_txn(self, account: Account, func: callable, args: tuple) -> SignedTransaction:
        call = func(*args)
        details = self._txn_details(account, call)
        txn = call.buildTransaction(details)
        return self.w3.eth.account.sign_transaction(txn, private_key=account.key)

    def _txn_details(self, account: Account, call: callable):
        return {
            "chainId" : self.chain_id,
            "gas" : self.gas(call),
            "gasPrice" : self.gas_price(),
            "nonce" : self.w3.eth.getTransactionCount(account.address),
        }

    def gas(self, call: callable) -> int:
        if self.config.get('transactions.gas.useEstimate'):
            return self._estimate_call_gas(call)
        return self.config.get('transactions.gas.exact')
    
    def _estimate_call_gas(self, call: callable) -> int:
        return int(call.estimateGas())

    def gas_price(self):
        return self.w3.toWei(
            self.config.get('transactions.gasPrice.number'), 
            self.config.get('transactions.gasPrice.unit')
        )
