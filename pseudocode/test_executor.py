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
    def receive(msg=('done', vc_config,), from_= p):
        output('Safety check 1: ', check_safety_1(vc_config))

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
        

