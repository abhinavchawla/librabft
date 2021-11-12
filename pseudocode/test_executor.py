class TestExecutor(Process):
    def setup(num_nodes, num_target_nodes, num_rounds, round_partitions:dict, round_leaders):
        self.public_keys_validators=[]
        self.private_keys_validators=[]
        self.validators = new(ValidatorX, num=num_nodes+num_target_nodes)
        self.playground = NetworkPlayground(num_nodes, num_target_nodes, num_rounds, round_partitions, validators)

    def run():        
        for _ in range(self.num_nodes):
            sk = SigningKey.generate()
            pk = sk.verify_key
            self.public_keys_validators.append(pk)
            self.private_keys_validators.append(sk)
        self.setupValidators()
        start(validators)
        start(playground)        
                
    def setupValidators(self):
        for i in range(self.num_nodes+num_target_nodes):
            if i >= num_nodes and i < num_nodes+num_target_nodes:               # Configure twins
                setup(self.validators[num_nodes+i], (public_keys_validators[i], private_keys_validators[i], public_keys_validators, self.round_leaders, playground))
            else:                                                               # Configure non-twins
                setup(self.validators[i], (public_keys_validators[i], private_keys_validators[i], public_keys_validators, self.round_leaders, playground))
            
    # Wait for done message from the network playground
    def receive(msg=('done', vc_config, gdcb_config), from_= p):
        output('Safety check 1: ', check_safety_1(vc_config))
        output('Safety check 2: ', check_safety_2(gdcb_config))

    '''
    Safety Property 1. If a block is certified in a round, no other block can gather 
    f + 1 non-Byzantine votes in the same round. Hence, at most one block is certified 
    in each round. To check the above property, we keep a count of votes per block-id, 
    per round. At the end this information, is passed on to the executor, which can 
    then check the safety.

        The structure of the vc_config is for every round r, we collect votes
        for each block-id in that round.
        {
            'r1':   {
                        'b_id1': {x1, x2, ...},
                        'b_id2': {y1, y2, ...},
                        ...
                    },
            ...
        }
    '''
    def check_safety_1(vc_config):
        for r in vc_config:                         
            certified_strong = False
            certified_weak = False
            for b in vc_config[r]:
                if len(vc_config[r][b]) >= 2*f+1:
                    certified_strong = True
                elif len(vc_config[r][b]) >= f+1:
                    certified_weak = True
                if certified_strong and certified_weak:
                    return False
        return True

    '''
    Property 2. For every two globally direct-committed blocks B, B0 , 
    either B ←−∗ B0 or B0 ←−∗ B.

    Definition 1 (Global direct-commit). We say that a block B is globally 
    direct-committed if f + 1 nonByzantine validators each call 
    Safety.make_vote on block B0 in round B.round + 1, such that B0 .QC 
    certifies B (i.e., B0 .QC = QCB), setting Safety.highest qc round ← B.round. 
    These calls return f + 1 matching votes (that could be used to form a 
    QCB0 with f other matching votes).

    The structure of the gdcb_config is for every round r, we collect votes
        for each block-id in that round.
        {
            'r1':   {
                        b_id1,b_id2,...
                    },
            ...
        }
    '''
    def check_safety_2(gdcb_config):
        gdc_blocks = []
        for r in gdcb_config:
            for b in gdcb_config[r]:
                if b in gdc_blocks:     
                    return False       # A block cannot be voted for in different rounds
                else:
                    gdc_blocks.add[b]

        # Check for every pair of blocks, one is the parent of other
        for i in enumerate(gdc_blocks):
            for j in range(i+1, gdc_blocks.len()):
                if not is_parent(gdc_blocks[i], gdc_blocks[j]) and not is_parent(gdc_blocks[j], gdc_blocks[i]): 
                    return False                

        return True
    
    # Check if b1 is parent of b2
    def is_parent(b1, b2):
        parent = b2.qc.vote_info.parent_id

        while not is_genesis_block(parent):     # Check if given block is a genesis block
            if parent == b1:
                return True
        return False
