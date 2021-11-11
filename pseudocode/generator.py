import random
from itertools import permutations

class scenario_generator():

	def get_partition_scenarios(n,type,x):
		partition_scenario_list=[]
		for i in range(1,n+1):
			partition_scenario_list+=recursion_sterling_set(len(n),i)
		pruned_partition_scenarios=prune(partition_scenario_list,type,x)
		return pruned_partition_scenarios

	def get_scenario_leaders(n,pruned_partition_scenarios,type,x,leader_type,twins):
		scenario_leaders={}
		twins_list=[]
		for node in n[len(n)-twins:]:
			twins_list.append(node)
		for i,scenario in enumerate(pruned_partition_scenarios):
			available_nodes=[]
			for partition in scenario:
				for node in partition:
					available_nodes.append(node)
			for node in available_nodes:
				if(leader_typer=="twin" and node in twins_list):
					scenario_leaders.append(node,i+1)
				elif(leader_typer!="twin" and node not in twins_list):
					scenario_leaders.append(node,i+1)
		pruned_scenario_leaders=prune(scenario_leaders,type,x)
		return pruned_scenario_leaders

	def leader_per_round_in_scenario(pruned_scenario_leaders,rounds):
		map={}
		leader_per_round=[]
		for scenario_leader in pruned_scenario_leaders:
			map[scenario_leader[1]].append(scenario_leader[0])
		for key,val in map.items():
			perm=permutations(val,rounds)
			leader_per_round.append(perm)
		return leader_per_round

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