"""
Queue object for Micilang

Poznámky:
__getitem__ se nepoužívá, řeší se jen první v pořadí
"""

class Queue():
    def __init__(self):
        self.content = [10, 24, 89]

    def __len__(self):
        return len(self.content)
    
    def __iter__(self):
        return iter(self.content)
    
    def peek(self):
        if not self.content:
            return None
        return self.content[0]
    
    def enqueue(self, element):
        self.content.append(element)

    def dequeue(self):
        self.content.pop(0)