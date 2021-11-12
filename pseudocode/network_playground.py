class Network_Playground(process):
    def setup(num_nodes, num_target_nodes, num_rounds, round_partitions:dict, validators:set):
        self.drop_config_round = None
        self.speculative_round = 0                  # Current round of the system, based on message intercepted
        self.twin_config = None
        self.vote_count_config = None
        self.gdcb_config = None
        self.done = False

    def run():
        populate_twin_config()
        populate_drop_config_round()

        while not done:                             # Stopping condition
            if speculative_round >= num_rounds+3:   # Over-guesstimating, when the round becomes num_rounds+3
                done = True                         # stop processing

        send (('done', vote_count_config), to=parent())                  # Send a message to parent, ie Executor to let it know of the processing stoppage

    '''
    A node checks the sender of a message based on the public key present in the message.
    When a node replies to a message, it sends a reply to the corresponding node of a public key.
    A node thus maintains a map of (publicKey, nodeId)
    The network playground would then check if the given node (identified by the nodeId), is present
    in the twin_config (ie, is a node with a twin). If the node has a twin, the message gets sent
    to the corresponding twin if the twin is present in the same partitions, or the node if it is present
    in the same partition as the sender, or to both the node and its twin, if all of the three are 
    present in the same partition.
    '''
    def receive(msg=('proposalMessageSent', m, to), from_= p): # eg received(('proposalMessageSent', (proposalMessage, msg, sender), to), from_=vX)
        (tag, p_msg) = m
        (block, _, _) = p_msg
        msg_round = block.round
        if not check_failure_config(tag, p, to):            # Check if the message is dropped according to the failure config
            return
        if to in twin_config:                               # Route message based on the twin_config
            twinId = twin_config[to]
            if not is_message_dropped(msg_round, p, to):
                send((tag, m), to=to)
            if not is_message_dropped(msg_round, p, twinId):
                send((tag, m), to=twinId)
        elif not is_message_dropped(msg_round, p, to):
            send((tag, m), to=to)
        if msg_round > speculative_round:
            speculative_round = msg_round


    '''
    Safety Property 1. If a block is certified in a round, no other block can gather f + 1 non-Byzantine votes in the
    same round. Hence, at most one block is certified in each round.
    To check the above property, we keep a count of votes per block-id, per round. At the end this information, 
    is passed on to the executor, which can then check the safety.
    '''
    def receive(msg=('voteMessageSent', m,), from_= p):
        (tag, v_msg) = m
        (v_info, _, _, _, _) = v_msg
        msg_round = v_info.round
        process_votes(v_info, sender)
        if not check_failure_config(tag, p, to, round):     # Check if the message is dropped according to the failure config
            return
        if to in twin_config:                               # Route message based on the twin_config
            twinId = twin_config[to]
            if not is_message_dropped(msg_round, p, to):
                send((tag, m), to=to)
            if not is_message_dropped(msg_round, p, twinId):
                send((tag, m), to=twinId)
        if not is_message_dropped(msg_round, p, to):
            send((tag, m), to=to)
        if msg_round > speculative_round:
            speculative_round = msg_round

    def receive(msg=('timeoutMessageSent', m,), from_= p):
        (tag, to_msg) = m
        (to_info, _, _, _, _) = to_msg
        msg_round = to_info.round
        if not check_failure_config(tag, p, to, round):    # Check if the message is dropped according to the failure config
            return
        if not is_message_dropped(msg_round, p, to):
            send((tag, m), to=to)
        if msg_round > speculative_round:
            speculative_round = msg_round

    def receive(msg=('initiateRecoverySent', m,), from_= p):
        (tag, n) = m
        if not is_message_dropped(speculative_round, p, to):
            send((tag, m), to=to)

    def receive(msg=('recoveryMsgSent', m), from_= p):
        (tag, r_msg, _, _) = m
        (_, _, _, pm_state, _) = r_msg
        msg_round = pm_state.pacemaker_current_round
        if not is_message_dropped(msg_round, p, to):
            send((tag, m, x, n), to=to)
        if msg_round > speculative_round:
            speculative_round = msg_round

    def is_message_dropped(round, src, dst):
        return dst in drop_config_round.find_or_return_false(round).find_or_return_false(src)

    def populate_drop_config_round():
        for round_key in round_partitions:
            partition_current = round_partitions[round_key]
            for i, partition in enumerate(partition_current):
                for src in partition:
                    for j in range(i+1, round_partitions[round_key].len):
                        for dst in round_partitions[round_key][j]:
                            split_network_round(src, dst, round_key)
                            split_network_round(dst, src, round_key)

    def split_network_round(src, dst, round):
        drop_config_round.find_or_create(round).find_or_create(src).add(dst) # adds {'r1':{'s1': {d1, d2, d3}} ... }

    '''
    Here, 
        map validator to its twin (A -> A')
        assuming, twins are enumerated beginning at the start of the 
        validator list. Eg, if there are two twins in the system,
        we can deduce twins to be, A', & B', ie, signifies the first 
        two nodes as having their twins in the system. This does not 
        hamper the generality of the system, as the scenario partitions
        generated would still be the same. Replacing A with D, and A' with D'
        amounts to have same effect.
    '''
    def populate_twin_config():
        for i in range (0, num_target_nodes):
            twin_config.add_or_update(validators[i], validators[num_nodes+i])

    def process_votes(v_info, sender):
        '''
        The structure of the vote_count_config is for every round r, we collect votes
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
        vote_count_config.find_or_create(v_info.round).find_or_create(v_info.id).add_to_set(sender)
