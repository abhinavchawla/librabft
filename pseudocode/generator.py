import random
from itertools import permutations

class scenario_generator():

	def run(self, config, fileName=None):
		if(fileName==None):
			scenarios=get_partition_scenarios(config.get("nodes"),config.get("type-step-1"),config.get("val-step-1"))
			scenario_leaders=get_scenario_leaders(config.get("nodes"),scenarios,config.get("type-step-2"),config.get("val-step-2"),
				config.get("leader_type"),config.get("twins"))
			leaders_per_round=leader_per_round_in_scenario(scenario_leaders,config.get("rounds"),config.get("type-step-1"),config.get("val-step-1"))
			writeToFile("leader_config", leaders_per_round, config.get("intraPartitionScenario"))
		else:
			leaders_per_round = readFromFile(fileName)
		return leaders_per_round

	# STEP 1: In this function we are generating all possible partition scenarios
	# we will use sterling's number of 2nd kind to get all possible partion scenarios
	# the reference for getting the sterling set is given in the pseudocode
	# we then use the prune function to remove unwanted partition scenarios
	def get_partition_scenarios(n,type,x):
		# generating all possible non-empty partitions ranging from 1 to n
		partition_scenario_list=[]
		for i in range(1,len(n)+1):
			partition_scenario_list+=recursion_sterling_set(len(n),i)
		# sending partition scenarios for pruning
		pruned_partition_scenarios=prune(partition_scenario_list,type,x)
		return pruned_partition_scenarios

	# STEP 2: In this function we'll get all possible leaders for a partition scenario
	# In this function we are getting the pruned list of partition scenarios
	# The leader_type parameter tells whether the leaders should be twins or original nodes
	# After checking the validity of a partition, we'll get all nodes in that scenrio
	# According to the found nodes and leader_type, we'll make a list of all possible leaders corresponding to a scenario
	# We'll prune this list of possible leaders using the prune function
	def get_scenario_leaders(n,pruned_partition_scenarios,type,x,leader_type,twins):
		scenario_leaders={}
		twins_list=[]
		# getting list of twins
		for node in n[len(n)-twins:]:
			twins_list.append(node)
		# iterating over all scenarios
		for i,scenario in enumerate(pruned_partition_scenarios):
			# checking the validity of the scenario
			if(not isValid(scenario,twins,n)):
				continue
			available_nodes=[]
			# iterating over all the partitions to get all possible nodes
			for partition in scenario:
				for node in partition:
					available_nodes.append(node)
			# if an available_node matches the leader_type argument, it is added to the list of possible leaders
			for node in available_nodes:
				if(leader_typer=="twin" and node in twins_list):
					scenario_leaders.append(node,i+1)
				elif(leader_typer!="twin" and node not in twins_list):
					scenario_leaders.append(node,i+1)
		# the list of possible leaders is sent for pruning
		pruned_scenario_leaders=prune(scenario_leaders,type,x)
		return pruned_scenario_leaders

	# This function checks if a scenario is valid
	# If the largest partition in the scanrio has nodes>=2f+1 then it is valid
	# If a node and its twin are in the same partition then it is invalid
	def isValid(scenario,twins,n):
		max_count=0
		max_partition=[]
		offset=len(n)-twins
		# getting the partition with the largest length
		for partition in scenario:
			max_count=max(max_count,len(partition))
			if(max_count<len(partition)):
				max_count=len(partition)
				max_partition=partition
		# checking the size of largest partition against 2f+1
		if(max_count>=(2*twins)+1):
			# checking if the partition contains both the original node and its twin
			for node in max_partition:
				index=n.index(node)
				if(index<offset and index+offset<len(n) and n[index+offset] in partition):
					return False
				elif(index>offset and index-offset>=0 and n[index-offset] in partition):
					return False
			return True
		else:
			return False

	# STEP 3: In this function we are generating all permutations of leaders according to the given rounds
	# All possible permutations of leaders over given rounds, for each scenario is calculated and returned as a list
	def leader_per_round_in_scenario(pruned_scenario_leaders,rounds, type, x, with_repetition=False):
		if with_repetition:
			perm=permutations(val,rounds)
		else:
			perm = [p for p in itertools.product(x, repeat=rounds)]
		return prune(perm, type, x)

	# This function prunes a list based on the type argument
	# type can be randomized or deterministic
	# Accordingly lists are pruned and returned
	def prune(givenList,type,x):
		if (type=="randomized"):
			pruned_list=[]
			for i in range(x):
				pruned_list.append(random.choice(givenList))
			return pruned_list
		elif (type=="deterministic"):
			return givenList[:x]
		else:
			return None

	#reference: https://stackoverflow.com/questions/54025505/find-all-possible-solutions-of-stirling-number-of-second-kind-using-python	
	def recursion_sterling_set(n,k):
		if k ==1:
			return [[[x for x in range(n)]]]
		elif n == k :
			return [[[x] for x in range(n)]]
		else:
			temp_n = n
			temp_k = k
			s_n_1_k_1 = recursion_sterling_set(temp_n-1,temp_k-1)
			for i in range(len(s_n_1_k_1)):
				s_n_1_k_1[i].append([temp_n-1])
			
			k_s_n_1_k= []
			temp = recursion_sterling_set(temp_n-1,temp_k)
			for i in range (k):
				temp_ = copy.deepcopy(temp)
				k_s_n_1_k += temp_
			for i in range(len(temp)*k):
				k_s_n_1_k[i][int(i/len(temp))] += [temp_n-1]
			
			return (s_n_1_k_1+k_s_n_1_k)