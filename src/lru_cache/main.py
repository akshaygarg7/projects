from typing import Any


class CacheNode:
    _key: Any
    _value: Any
    _prev: CacheNode
    _next: CacheNode

    def __init__(self, key, value):
        self._key = key
        self._value = value
        self._next = None
        self._prev = None

    def get(self):
        return self._value;

    def key(self):
        return self._key;

class LRUCache:
    _capacity: int
    _key_node_map: dict
    _head: CacheNode
    _tail: CacheNode
    
    def __init__(self, capacity):
        self._capacity = capacity
        self._key_node_map = {}
        self._head = None
        self._tail = None

    def move_to_front(self, node: CacheNode):
        # detach node
        if node._next == None:
           self._tail = node._prev
           self._tail._next = None
        elif node._prev == None:
           return 
        else:
            node._next._prev = node._prev
            node._prev._next = node._next

        # update head
        node._next = self._head
        self._head._prev = node
        node._prev = None
        self._head = node
        

    def put(self, key, value):
        # if key exists, update value, move node to top
        # if size full, delete last element
        node = None
        if self._key_node_map.get(key) is None:
            if self.size() == self._capacity:
                node_to_delete = self._tail
                
                self._tail = node_to_delete._prev
                self._tail._next = None 
                node_to_delete._prev = None                

                self._key_node_map.pop(node_to_delete.key())

            node = CacheNode(key, value)
            self._key_node_map[key] = node
        else:
            node = self._key_node_map["key"]
            node._value = value
        
        if self.size() == 1:
            self._head = node
            self._tail = node
            return
        else:
            self._tail._next = node
            node._prev = self._tail
            self._tail = node

        # self.printAll()
        self.move_to_front(node)

        return None
    
    def get(self, key):
        node = self._key_node_map[key] 
        
        if node:
            self.move_to_front(node)
            return node.get()
        else:
            return None
        
    def printAll(self):
        chain = ""
        node = self._head
        while(node != None):
            chain = chain + node.get() + "->"
            node = node._next
        print(chain)

        node = self._tail
        chain = ""
        while(node != None):
            chain = chain + node.get() + "->"
            node = node._prev
        print(chain)
    
    
    def size(self):
        return len(self._key_node_map)

    
if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put("name", "akshay garg")
    cache.put("address", "Delhi")
    cache.put("email", "abcd")
    print(cache.get("address"))
    cache.put("phone", "1234")