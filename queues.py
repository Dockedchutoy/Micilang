"""
Queue object for Micilang

Poznámky:
__getitem__ se nepoužívá, řeší se jen první v pořadí
"""

from collections import deque

tokens = deque([deque([20, 10]), deque([30, 40])])

def token():
    return tokens[0]

print(token())
token().popleft()
print(token()[0])

class Queue():
    def __init__(self, elements=None):
        self.content = []
        if elements:
            for element in elements:
                self.content.append(element)

    def __len__(self):
        return len(self.content)
    
    def __iter__(self):
        return iter(self.content)
    
    def __str__(self):
        return f"<{', '.join(str(element) for element in self)}>"
    
    def __repr__(self):
        return f"<{', '.join(repr(element) for element in self)}>"
    
    def peek(self):
        if not self.content:
            return None
        return self.content[0]
    
    def enqueue(self, element):
        self.content.append(element)

    def dequeue(self):
        self.content.pop(0)