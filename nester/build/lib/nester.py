"""
This is a "nester.py" module, and it provides one function called 
print_lol() which prints list that may or maynot include nested list
"""
def print_lol(the_list):
	"""
	This function takes positional argument called "the_list", whcih is any python
	list (of possibly nested list). Each data item in the provided list is (recursively)
	printed to the screen on its own line
	"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
