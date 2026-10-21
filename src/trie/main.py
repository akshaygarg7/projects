import math
import time
from threading import Lock
from typing import Callable


class TrieNode:
	def __init__(self):
		self.children = {}
		self.is_end_of_word = False

class Trie:
	root = None

	def __init__(self):
		self.root = TrieNode()

	def insert(self, word):
		current = self.root
		for ch in word:
			if ch not in current.children:
				new_node = TrieNode()
				current.children[ch] = new_node
			current = current.children[ch]
		current.is_end_of_word = True

	def exists(self, word):
		current = self.root
		found = False
		for ch in word:
			if ch not in current.children:
				break
			else:
				current = current.children[ch]
		if current.is_end_of_word:
			found = True
		return found

	def search(self, prefix):
		current = self.root
		result = []
		for ch in prefix:
			if ch not in current.children:
				return None
			current = current.children[ch]

		self.getWords(current, prefix, result)
		return result

	def getWords(self, node, word, result):
		# print(node)
		if node.is_end_of_word:
			result.append(word)
		
		for ch, node in node.children.items():
			self.getWords(node, word + ch, result)
				
	def print(self):
		result = []
		self.getWords(self.root, "", result)
		print(result)


if __name__ == "__main__":
	trie = Trie()
	# trie.print()

	trie.insert("sea")
	trie.insert("cat")
	trie.insert("cattle")
	trie.insert("seat")

	# trie.print()
	# print(trie.exists("sea"))
	print(trie.search("se"))