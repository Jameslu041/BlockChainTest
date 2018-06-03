"""
author: james lu
start_time: 2018.05.07

"""

import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # genesis block
        self.new_block(previous_hash=41, proof=100)

    def new_block(self, proof, previous_hash):
        # create a new block and add it to chain.
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transactions(self, sender, recipient, amount):
        # add a new transaction to the list of transaction
        """
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a block
        block_string = json.dump(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # return the last block in the chain
        return self.chain[-1]

    # PoW
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '') # generate a unique address
blockchain = Blockchain()

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Welcome to Jamie's BlockChain~"

@app.route('/mine', methods=['GET'])
def mine():
    # using PoW to get next block
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # give a reward for finding the proof
    blockchain.new_transactions(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )
    block = blockchain.new_block(last_proof, proof)

    response = {
        'message': "New Block Get",
        'index': block['index'],
        'transaction': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # if values is None:
    #     return request.get_data()

    required = ['sender', 'recipient', 'amount']
    if not all([k in values for k in required]):
        return 'Missing values', 400

    index = blockchain.new_transactions(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be add to Block{index}'}

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)