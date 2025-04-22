from sydney_transport.binary_tree.node import Node
from sydney_transport.stop import Stop

class AvlTree:
    def __init__(self):
        self.root = None

    def insert(self, stop: Stop, travel_time):
        # empty tree
        if self.root is None:
            self.root = Node(stop, travel_time)
            return

        curr_node = self.root
        final_node = None

        while True:
            # insert left
            if travel_time < curr_node.travel_time and curr_node.left is None:
                new_node = Node(stop, travel_time)
                curr_node.left = new_node
                new_node.parent = curr_node
                curr_node.height += 1
                final_node = new_node
                break
            # insert right
            elif travel_time > curr_node.travel_time and curr_node.right is None:
                new_node = Node(stop, travel_time)
                curr_node.right = new_node
                new_node.parent = curr_node
                curr_node.height -= 1
                final_node = new_node
                break
            # insert in current node
            elif travel_time == curr_node.travel_time:
                curr_node.stops.append(stop)
                final_node = curr_node
                break

            # traverse left branch
            if travel_time < curr_node.travel_time:
                curr_node.height += 1
                curr_node = curr_node.left
                continue
            # traverse right branch
            elif travel_time > curr_node.travel_time:
                curr_node.height -= 1
                curr_node = curr_node.right
                continue

        self._balance_tree(final_node)

    def _balance_tree(self, node: Node):
        curr_node = node
        while True:
            # branch is right heavy
            if curr_node.height < -1:
                right_child: Node = curr_node.right

                if right_child.right:
                    curr_node = self._left_rotation(curr_node)
                elif right_child.left:
                    curr_node = self._right_left_rotation(curr_node)
            # branch if left heavy
            elif curr_node.height > 1:
                left_child: Node = curr_node.left

                if left_child.left:
                    curr_node = self._right_rotation(curr_node)
                elif left_child.right:
                    curr_node = self._left_right_rotation(curr_node)

            if curr_node.parent is None:
                return

            curr_node = curr_node.parent

    def _left_rotation(self, z: Node) -> Node:
        y = z.right

        # replace z with y
        y.parent = z.parent
        if y.parent is not None:
            y.parent.right = y
        else:
            self.root = y

        # set T1 to z
        y.left = z
        z.right = None

        # reset heights
        z.height = 0
        y.height = 0

        return y

    def _right_rotation(self, z: Node) -> Node:
        y = z.left

        # replace z with y
        y.parent = z.parent
        if y.parent is not None:
            y.parent.left = y
        else:
            self.root = y

        # set T1 to z
        y.right = z
        z.left = None

        # reset heights
        z.height = 0
        y.height = 0

        return y

    def _left_right_rotation(self, z: Node) -> Node:
        y = z.left
        x = y.right

        # switching x and z
        x.parent = z.parent
        if x.parent is not None:
            x.parent.left = x
        else:
            self.root = x

        # connect y to x
        y.parent = x
        x.left = y
        y.right = None

        # connect z to x
        z.parent = x
        x.right = z
        z.left = None

        return x

    def _right_left_rotation(self, z: Node) -> Node:
        y = z.right
        x = y.left

        # switching x and z
        x.parent = z.parent
        if x.parent is not None:
            x.parent.right = x
        else:
            self.root = x

        # connect y to x
        y.parent = x
        x.right = y
        y.left = None

        # connect z to x
        z.parent = x
        x.left = z
        z.right = None

        return x

    def get_shortest_stop(self):
        if self.root is None:
            return

        curr_node = self.root

        # find the furthest left node
        while True:
            if curr_node.left is None:
                break

            curr_node = curr_node.left

        if len(curr_node.stops) == 1:
            curr_node.parent.height -= 1

            right_node = curr_node.right
            if right_node is not None:
                right_node.parent = curr_node.parent
                right_node.parent.left = right_node

            self._balance_tree(right_node)

        return curr_node.stops.pop(0)
