from node import Node

class LinkedList:
    def __init__(self, begin = None):
        self.length = 0
        self.begin  = begin
        self.end    = begin

    def add_node(self, data):
        if self.length == 0:
            n = Node(data)
            self.begin = n
            self.end = n
        else:
            n = Node(data, None, self.begin)
            self.begin.prev_node = n
            self.begin = n
        self.length += 1

    def remove_node(self, data):
        current_node = self.begin

        if self.end is not None:
            if data == self.end.get_data():
                current_node = self.end

        while current_node is not None:
            if current_node.get_data() == data:
                if current_node.get_prev_node() is not None:
                    # current_node is between other nodes
                    if current_node.get_next_node():
                        prev_node = current_node.get_prev_node()
                        next_node = current_node.get_next_node()
                        prev_node.set_next_node(next_node)
                        next_node.set_prev_node(prev_node)
                    # current_node is at the end
                    else:
                        prev_node = current_node.get_prev_node()
                        prev_node.set_next_node(None)
                        self.end = prev_node
                else:
                # current_node is at the start
                    self.begin = current_node.get_next_node()

                    if self.length == 1:
                        self.end = self.begin
                    else:
                        current_node.get_next_node().set_prev_node(None)

                self.length -= 1
                return True
            else:
                current_node = current_node.get_next_node()

        return False

    def get_length(self):
        return self.length
