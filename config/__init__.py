import time

def validate_transaction(tx_hash,w3,TARGET_CONTRACT_ADDRESS):
    try:
        tx_hash = tx_hash.lower()
        
        if not tx_hash.startswith('0x'):
            tx_hash = '0x' + tx_hash
            
        tx = w3.eth.get_transaction(tx_hash)
        if tx is None:
            return False, "Transaction not found", None
            
        sender_address = tx['from'].lower()
            
        if tx.blockNumber is None:
            return False, "Transaction is not confirmed yet", None
            
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt.status != 1:
            return False, "Transaction failed", None
            
        
        if tx.to is None or tx.to not in TARGET_CONTRACT_ADDRESS:
            return False, f"Transaction does not interact with the target contract", None
            
        block = w3.eth.get_block(tx.blockNumber)
        block_timestamp = block.timestamp
        
        current_time = int(time.time())

        if current_time - block_timestamp > 60:  
            return False, "Transaction is older than 1 minute", None
            
        return True, None, sender_address
        
    except Exception as e:
        return False, f"Error validating transaction: {str(e)}", None