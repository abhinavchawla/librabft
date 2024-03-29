import random
from itertools import permutations, product, chain, combinations
import copy
import json

class scenario_generator():

	def __init__(self, fileName=None, config=None):
		if(fileName==None):
			self.nodes = config.get("nodes")
			self.twins = config.get("twins")
			self.rounds = config.get("rounds")
			scenarios=self.get_partition_scenarios(config.get("nodes"),config.get("twins"),config.get("step-1"), config.get("intra-partition-config"))
			scenario_leaders=self.get_scenario_leaders(scenarios, config.get("nodes"),config.get("twins"),config.get("step-2"))
			leaders_per_round=self.leader_per_round_in_scenario(scenario_leaders, config.get("rounds"), config.get("step-3"))
			print(leaders_per_round)
			self.json_dict = self.create_json_dict(leaders_per_round, config.get("nodes"), config.get("twins"), config.get("rounds"))
			with open('data.json', 'w') as f:
				json.dump(self.json_dict, f, indent=4)
		else:
			with open(fileName,'r') as f:
				self.json_dict = json.load(f)
				self.nodes = self.json_dict['nodes']
				self.twins = self.json_dict['twins']
				self.rounds = self.json_dict['rounds']
		self.current_scenario_index = 0
	def generate_scenario(self):
		if self.current_scenario_index < len(self.json_dict['scenarios']):
			scenario = self.json_dict['scenarios'][self.current_scenario_index]
			self.current_scenario_index += 1
			scenario['nodes'] = self.nodes
			scenario['twins'] = self.twins
			scenario['rounds'] = self.rounds
			return scenario
		else:
			return None

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
			tmp_mp['message-drops'] = {}
			for j in range(len(leaders_per_round[i])):
				tmp_mp['leaders'][str(j+1)] = leaders_per_round[i][j][0]
			for j in range(len(leaders_per_round[i])):
				tmp_mp['partitions'][str(j+1)] = leaders_per_round[i][j][1][0]
			for j in range(len(leaders_per_round[i])):
				tmp_mp['message-drops'][str(j+1)] = leaders_per_round[i][j][1][1]
			json_dict['scenarios'].append(tmp_mp)
		return json_dict
	def run(self, config, fileName=None):
		pass

	# STEP 1: In this function we are generating all possible partition scenarios
	# we will use sterling's number of 2nd kind to get all possible partion scenarios
	# the reference for getting the sterling set is given in the pseudocode
	# we then use the prune function to remove unwanted partition scenarios
	def get_partition_scenarios(self,n,twins,config, intra_partition_config):
		# generating all possible non-empty partitions ranging from 1 to n
		partition_scenario_list=[]
		for i in range(1,n+twins+1):
			tmp_lst = self.recursion_sterling_set(n+twins,i)
			for i in tmp_lst:
				if self.isValid(i,twins,n):
					partition_scenario_list.append(i)
		intra_partition_scenario_list = []
		for scenario in partition_scenario_list:
			intra_partition_scenario_list+=self.create_intra_partition_scenarios(scenario, intra_partition_config)
		print(len(intra_partition_scenario_list))
		# sending partition scenarios for pruning
		if config.get("prune") ==True:
			pruned_partition_scenarios=self.prune(partition_scenario_list,config.get("type"),config.get("value"))
			return pruned_partition_scenarios
		return intra_partition_scenario_list
	
	def create_intra_partition_scenarios(self, scenario, config):
		res = []
		dropped_messages = config.get("message-drops")		
		message_drops_combinations = list(chain.from_iterable(combinations(dropped_messages,r) for r in range(len(dropped_messages)+1)))
		max_message_drops = config.get("max-message-drops")
		
		for comb in message_drops_combinations:
			if len(comb) > max_message_drops:
				message_drops_combinations.remove(comb)
		tmp = [message_drops_combinations]*len(scenario)
		cart_product = list(product(*tmp))
		for i in range(len(cart_product)):
			res.append((scenario,cart_product[i]))
		return res

		# print(message_drops_combinations)
			
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
		# getting the partition with the largest length
		for partition in scenario:
			if(max_count<len(partition)):
				max_count=len(partition)
				max_partition=partition
		# checking the size of largest partition against 2f+1
		if(max_count>=(2*twins)+1):
			# checking if the partition contains both the original node and its twin
			cnt = 0
			for i in range(len(max_partition)):
				if max_partition[i] < n:
					cnt+=1
				elif max_partition[i] - n not in max_partition:
					cnt+=1
			if cnt>=(2*twins)+1:
				return True
			else:
				return False
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
			pruned_partition_scenarios=self.prune(perm_lst,config.get("type"),config.get("value"))

			for j in range(len(pruned_partition_scenarios)):
				print(j)
				round_lst=copy.deepcopy(list(pruned_partition_scenarios[j]))

				for i in range(7,10):
					round=copy.deepcopy(list(round_lst[i]))
					round_details=copy.deepcopy(list(round[1]))
					drop_list=copy.deepcopy(list(round_details[1]))
					drop_list.clear()
					drop_list=tuple(drop_list)
					drop_list+=()
					round_details[0].clear()
					round_details[0].append([0,1,2,3,4])
					round_details[1]=drop_list
					round[1]=tuple(round_details)
					round_lst[i]=tuple(round)
				pruned_partition_scenarios[j]=tuple(round_lst)
				#print(pruned_partition_scenarios[j])

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