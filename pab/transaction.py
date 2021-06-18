import logging

from web3 import Web3
from hexbytes import HexBytes
from eth_account.datastructures import SignedTransaction

from pab.config import APP_CONFIG


class TransactionError(Exception): 
    pass


class TransactionHandler:
    def __init__(self, w3: Web3, chain_id: int, gas: int = 1, owner: str = None, private_key: HexBytes = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.w3 = w3
        self.owner = owner
        self.private_key = private_key
        self.chain_id = chain_id
        self.gas = gas
        
    def transact(self, func: callable, args: tuple, timeout: int = APP_CONFIG.get("transactionTimeout", 200)):
        """ Submits transaction and prints hash """
        if not self.private_key:
            raise TransactionError("Private key not set")
        stxn = self._build_signed_txn(func, args)
        sent = self.w3.eth.send_raw_transaction(stxn.rawTransaction)
        rcpt = self.w3.eth.wait_for_transaction_receipt(sent, timeout=timeout)
        self.logger.info(f"Block Hash: {rcpt.blockHash.hex()}")
        self.logger.info(f"Gas Used: {rcpt.gasUsed}")
        return sent, rcpt
    
    def _build_signed_txn(self, func: callable, args: tuple) -> SignedTransaction:
        call = func(*args)
        details = self._txn_details(call)
        txn = call.buildTransaction(details)
        return self.w3.eth.account.sign_transaction(txn, private_key=self.private_key)

    def _txn_details(self, call: callable):
        return {
            "chainId" : self.chain_id,
            "gas" : self._estimate_call_gas(call),
            "gasPrice" : self.w3.toWei('1', 'gwei'),
            "nonce" : self.w3.eth.getTransactionCount(self.owner),
        }

    def _estimate_call_gas(self, call: callable) -> int:
        return int(call.estimateGas())
