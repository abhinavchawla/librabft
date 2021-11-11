class TestExecutor(Process):
    def __init__(self, scenario)
        self.playground = NetworkPlayground()
    
    def run(self, scenario):
        self.num_of_nodes = scenario.nodes
        self.num_of_twins = scenario.twins
        self.round_leaders = scenario.round_leaders
        self.round_partitions = scenario.round_partitions
        self.public_keys_validators=[]
        self.private_keys_validators=[]
        self.validators = new(ValidatorX, num=nvalidators)
        for _ in range(self.num_of_nodes):
            sk = SigningKey.generate()
            pk = sk.verify_key
            self.public_keys_validators.append(pk)
            self.private_keys_validators.append(sk)
        self.setupValidators()
        start(self.validators)
        start(self.playground)
        
        

    def setupValidators(self):
        for i in range(self.num_of_nodes):
            setup(self.validators[i], (public_keys_validators[i], private_keys_validators[i], public_keys_validators, self.round_leaders))
            if i <num_of_twins:
                setup(self.validators[num_of_nodes+i], (public_keys_validators[i], private_keys_validators[i], public_keys_validators, self.round_leaders))
                