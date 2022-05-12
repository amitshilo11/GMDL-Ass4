import numpy as np

class Adder:
	def __init__(self, variable, const):
		self.variable = variable
		self.const = const
		self.val = 0
		self.next = None

	def reset(self):
		self.val = 0

		if self.next is not None:
			self.next.reset()
			
	def set_next(self, nextvar):
		self.next = nextvar

	def get_next_const(self):
		return self if self.const else (self.next.get_next_const() if self.next is not None else None)

	def inc(self):
		carry = False

		if self.const:
			carry = True
		else:
			self.val += 1

			if self.val == self.variable.num_of_states:
				self.val = 0
				carry = True
		
		if carry and self.next is not None:
			self.next.inc()
	
	def to_tuple(self):
		return tuple(self.to_list())

	def to_list(self):
		return [self.val] + (self.next.to_list() if self.next is not None else [])


class Node:
	def __init__(self, name):
		self.name = name
		self.neighbors = None

	def get_message_from_neighbor(self, neighbor):
		return neighbor.send_message_to(self)


class VariableNode(Node):
	def __init__(self, name, num_of_states):
		super().__init__(name)
		self.num_of_states = num_of_states
	
	def send_message_to(self, factor):
		# Messages from leaf variable nodes are initialized to unity.
		if len(self.neighbors) == 1:
			return np.ones(self.num_of_states)

		# This implements the Variable to Factor message formula.
		# We assume that when the graph was built, VariableNodes were only given FactorNode neighbors.
		msgs = np.array([self.get_message_from_neighbor(neighbor) for neighbor in self.neighbors if neighbor.name != factor.name])
		return msgs.prod(axis=0)

	# The Marginal formula from the PS.
	def marginal(self):
		msgs = np.array([self.get_message_from_neighbor(neighbor) for neighbor in self.neighbors])
		marginal_unnormalized = msgs.prod(axis=0)
		return marginal_unnormalized / marginal_unnormalized.sum()


class FactorNode(Node):
	def __init__(self, name, func):
		super().__init__(name)
		self.func = func

	def make_adder(self, excluded_neighbor):
		adders = [Adder(neighbor, neighbor.name == excluded_neighbor.name) for neighbor in self.neighbors]

		for i in range(len(adders) - 1):
			adders[i].set_next(adders[i + 1])

		return adders[0]

	def send_message_to(self, variable):
		# Messages from leaf factor nodes are initialized to the factor.
		if len(self.neighbors) == 1:
			return self.func

		# We assume that when the graph was built, FactorNodes were only given VariableNode neighbors.
		relevant_neighbors = [neighbor for neighbor in self.neighbors if neighbor.name != variable.name]
		msgs = [self.get_message_from_neighbor(neighbor)
				if neighbor.name != variable.name
				else None
				for neighbor in self.neighbors
				]
		num_of_combinations = np.prod(np.array([neighbor.num_of_states for neighbor in relevant_neighbors]))
		adder = self.make_adder(variable)
		ret_msg = np.zeros(variable.num_of_states)

		for var_state in range(variable.num_of_states):
			adder.reset()
			adder.get_next_const().val = var_state
			summands = []

			for _ in range(num_of_combinations):
				states = adder.to_tuple()
				msgs_prod = np.prod(np.array([msgs[i][states[i]] for i in range(len(self.neighbors)) if msgs[i] is not None]))
				summands.append(self.func[states] * msgs_prod)
				adder.inc()
			
			ret_msg[var_state] = np.sum(np.array(summands))
		
		return ret_msg

# Adding variable nodes.
D = VariableNode("D", 2)
I = VariableNode("I", 2)
G = VariableNode("G", 3)
S = VariableNode("S", 2)
L = VariableNode("L", 2)

# Adding factor nodes.
p_d = FactorNode("p_d", np.array([0.6, 0.4]))
p_i = FactorNode("p_i", np.array([0.7, 0.3]))
p_g_given_id = FactorNode("p_g_given_id",
						np.array([  [[0.3, 0.05], [0.9, 0.5]],
									[[0.4, 0.25], [0.08, 0.3]],
									[[0.3, 0.70], [0.02, 0.]],
								]))

p_s_given_i = FactorNode("p_s_given_i",
						np.array([  [0.95, 0.02],
                            		[0.05, 0.8]
						]))

p_l_given_g = FactorNode("p_l_given_g", 
						np.array([  [0.1, 0.4, 0.99],
                            		[0.9, 0.6, 0.01]
                        ]))

# Adding neighbors to variable nodes.
D.neighbors = [p_d, p_g_given_id]
I.neighbors = [p_i, p_g_given_id]
G.neighbors = [p_g_given_id, p_l_given_g]
S.neighbors = [p_s_given_i]
L.neighbors = [p_l_given_g]

# Adding neighbors to factor nodes.
p_d.neighbors = [D]
p_i.neighbors = [I]
p_g_given_id.neighbors = [G, I, D]
p_s_given_i.neighbors = [S, I]
p_l_given_g.neighbors = [L, G]

# Computing marginals.
print("p(d): ", D.marginal())
print("p(i): ", I.marginal())
print("p(g): ", G.marginal())
print("p(s): ", S.marginal())
print("p(l): ", L.marginal())