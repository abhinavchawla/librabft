import random
from itertools import permutations, product
import copy
import json

class scenario_generator():

	def __init__(self, fileName=None, config=None):
		if(fileName==None):
			scenarios=self.get_partition_scenarios(config.get("nodes"),config.get("twins"),config.get("step-1"))
			print(scenarios)
			scenario_leaders=self.get_scenario_leaders(scenarios, config.get("nodes"),config.get("twins"),config.get("step-2"))
			print(scenario_leaders)
			leaders_per_round=self.leader_per_round_in_scenario(scenario_leaders, config.get("rounds"), config.get("step-3"))
			print(leaders_per_round)
			json_dict = self.create_json_dict(leaders_per_round, config.get("nodes"), config.get("twins"), config.get("rounds"))
			with open('data.json', 'w') as f:
				json.dump(json_dict, f)
		else:
			leaders_per_round = readFromFile(fileName)
		return leaders_per_round
	
	def create_json_dict(self,leaders_per_round, nodes, twins, rounds):
		json_dict={}
		json_dict['nodes'] = nodes
		json_dict['twins'] = twins
		json_dict['rounds'] = rounds
		json_dict['scenarios'] = [] 
		for i in range(len(leaders_per_round)):
			tmp_mp = {}
			tmp_mp['leaders'] = {}
			tmp_mp['partitions'] = {}
			for j in range(len(leaders_per_round[i])):
				tmp_mp['leaders'][str(j)] = leaders_per_round[i][j][0]
			for j in range(len(leaders_per_round[i])):
				tmp_mp['partitions'][str(j)] = leaders_per_round[i][j][1]
			json_dict['scenarios'].append(tmp_mp)
		return json_dict
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
	def get_partition_scenarios(self,n,twins,config):
		# generating all possible non-empty partitions ranging from 1 to n
		partition_scenario_list=[]
		for i in range(1,n+twins+1):
			tmp_lst = self.recursion_sterling_set(n+twins,i)
			for i in tmp_lst:
				if self.isValid(i,twins,n):
					partition_scenario_list.append(i)
		
		# sending partition scenarios for pruning
		if config.get("prune") ==True:
			pruned_partition_scenarios=self.prune(partition_scenario_list,config.get("type"),config.get("value"))
			return pruned_partition_scenarios
		return partition_scenario_list
	# STEP 2: In this function we'll get all possible leaders for a partition scenario
	# In this function we are getting the pruned list of partition scenarios
	# The leader_type parameter tells whether the leaders should be twins or original nodes
	# After checking the validity of a partition, we'll get all nodes in that scenrio
	# According to the found nodes and leader_type, we'll make a list of all possible leaders corresponding to a scenario
	# We'll prune this list of possible leaders using the prune function
	def get_scenario_leaders(self, scenarios, n, twins, config):
		scenario_leaders=[]
		# iterating over all scenarios
		for i,scenario in enumerate(scenarios):
			total_leaders = n
			if(config.get("leader_type")=="twin"):
				total_leaders=twins
			for node in range(total_leaders):
					scenario_leaders.append((node,scenario))
		# the list of possible leaders is sent for pruning
		if config.get("prune") ==True:
			pruned_partition_scenarios=self.prune(scenario_leaders,config.get("type"),config.get("value"))
			return pruned_partition_scenarios
		return scenario_leaders


	# This function checks if a scenario is valid
	# If the largest partition in the scanrio has nodes>=2f+1 then it is valid
	# If a node and its twin are in the same partition then it is invalid
	def isValid(self,scenario,twins,n):
		max_count=0
		max_partition=[]
		offset=n-twins
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
	def leader_per_round_in_scenario(self,scenario_leaders,rounds, config):
		if not config.get("with-repetition"):
			perm=permutations(scenario_leaders,rounds)
			perm_lst = list(perm)
		else:
			perm = [p for p in product(scenario_leaders, repeat=rounds)]
		if config.get("prune") ==True:
			print(len(perm_lst))
			pruned_partition_scenarios=self.prune(perm_lst,config.get("type"),config.get("value"))
			return pruned_partition_scenarios
		return perm

	# This function prunes a list based on the type argument
	# type can be randomized or deterministic
	# Accordingly lists are pruned and returned
	def prune(self,givenList,type,x):
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
	def recursion_sterling_set(self,n,k):
		if k ==1:
			return [[[x for x in range(n)]]]
		elif n == k :
			return [[[x] for x in range(n)]]
		else:
			temp_n = n
			temp_k = k
			s_n_1_k_1 = self.recursion_sterling_set(temp_n-1,temp_k-1)
			for i in range(len(s_n_1_k_1)):
				s_n_1_k_1[i].append([temp_n-1])
			
			k_s_n_1_k= []
			temp = self.recursion_sterling_set(temp_n-1,temp_k)
			for i in range (k):
				temp_ = copy.deepcopy(temp)
				k_s_n_1_k += temp_
			for i in range(len(temp)*k):
				k_s_n_1_k[i][int(i/len(temp))] += [temp_n-1]
			
			return (s_n_1_k_1+k_s_n_1_k)