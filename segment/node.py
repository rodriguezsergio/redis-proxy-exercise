class Node:
    def __init__(self, data, prev_node = None, next_node = None):
        self.data     = data
        self.prev_node = prev_node
        self.next_node = next_node

    def get_prev_node(self):
        return self.prev_node

    def get_next_node(self):
        return self.next_node

    def get_data(self):
        return self.data

    def set_prev_node(self, node):
        self.prev_node = node

    def set_next_node(self, node):
        self.next_node = node

    def set_data(self, data):
        self.data = data
