# Module 2 - Create a Cryptocurrency called Charfaoui Coin (Chacoin)

#importing the libraries
import datetime
import hashlib
import json
from flask import Flask , jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        # the nodes containig our blockchain
        self.nodes = set()
        
    # this is a type general block , we can add anything
    def create_block(self, proof, previous_hash):
        block = { 'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions': self.transactions}
        self.transactions =  []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # operation must not be symetrical
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation  = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # function to uniform the adding transaction process in each node. 
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    # function that add a node to the nodes set.
    def add_node(self, address):
        # we get the address and parsed it.
        parsed_url = urlparse(address)
        
        # Then we take the netloc of the adress and add to the set.
        # example of netloc "https://127.0.0.1:5000/" netloc is "127.0.0.1:5000"
        self.nodes.add(parsed_url.netloc)
     
    # function that make concencus over the network of nodes.
    def replace_chain(self):
        # getting all the nodes
        network = self.nodes
        
        # creating variables to hold reference to the bigest chain and it's length
        longest_chain = None
        max_length = len(self.chain)
        for nodes in network:
            
            # requesting the chain in every node
            response = requests.get(f'http://{node}/get_chain')
            
            if response.status_code == 200:
                # getting the chain and the length of it in the current node
                length = response.json()['length']
                chain =response.json()['chain']
                
                # if the case that the current chain is bigger than the old one we update
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        # if the longest chain was updated then we update our chain.
        if longest_chain:
            self.chain = longest_chain
            # and we return true.
            return True
        return False

# Part 2 - Mining our Blockchain

# Creating web app
app = Flask(__name__)

# Creating an address for the node on Port 5000.
# we need the address to reward him with chacoin.
node_adress = str(uuid4()).replace('-','')
   
# Create a blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Younes', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Getting Full blockchain
@app.route('/get_chain',methods = ['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

#Running the app
app.run(host = '0.0.0.0' , port = 5000)
