from datetime import timedelta

from sydney_transport.binary_tree.node import Node
from sydney_transport.components.stop import Stop

class AvlTree:
    def __init__(self):
        self.root = None

    def __str__(self):
        return f""

    def inorder_traversal(self, node: Node):
        """
        Recursively performs an inorder traversal of the AVL Tree.
        """
        visited_nodes = []

        # tree is empty
        if node is None:
            return visited_nodes

        # traverse left and right branch
        left_branch = self.inorder_traversal(node.left)
        right_branch = self.inorder_traversal(node.right)

        visited_nodes = left_branch + [node.stops[0].stop_name] + right_branch

        return visited_nodes

    def _inorder_traversal2(self, node: Node):
        visited_nodes = []

        # tree is empty
        if node is None:
            return [None]

        # is leaf node
        if not node.left and not node.right:
            return [node.travel_time]

        # traverse left branch
        if node.left:
            visited_nodes += self.inorder_traversal(node.left)
        # traverse root
        visited_nodes += [node.travel_time]
        # traverse right branch
        if node.right:
            visited_nodes += self.inorder_traversal(node.right)

        return visited_nodes

    def _breadth_first_search(self, node: Node):
        node_queue = [(node, 0)]
        visited_nodes = []

        while len(node_queue) >= 1:
            next_in_queue = node_queue.pop(0)
            visited_nodes.append(next_in_queue)
            curr_node: Node = next_in_queue[0]
            curr_height = next_in_queue[1]

            if curr_node.left:
                node_queue.append((curr_node.left, curr_height + 1))
            if curr_node.right:
                node_queue.append((curr_node.right, curr_height + 1))

        return visited_nodes

    def insert(self, stop: Stop, travel_time: timedelta):
        new_node = Node(stop, travel_time)

        # empty tree
        if self.root is None:
            self.root = new_node
            return

        curr_node: Node = self.root

        # loop through nodes till a valid insertion location is found
        while True:
            # insert left
            if travel_time < curr_node.travel_time and curr_node.left is None:
                curr_node.left = new_node
                new_node.parent = curr_node
                break
            # insert right
            if travel_time > curr_node.travel_time and curr_node.right is None:
                curr_node.right = new_node
                new_node.parent = curr_node
                break
            # insert in current node
            if travel_time == curr_node.travel_time:
                curr_node.stops.append(stop)
                new_node = curr_node
                break

            # traverse left branch
            if travel_time < curr_node.travel_time:
                curr_node = curr_node.left
            # traverse right branch
            elif travel_time > curr_node.travel_time:
                curr_node = curr_node.right

        self._recalculate_height_and_balance_factor(new_node)
        self._balance_tree(new_node)

    def _recalculate_height_and_balance_factor(self, node: Node):
        while True:
            left_height = 0
            right_height = 0

            if node.left:
                left_height = node.left.height
            if node.right:
                right_height = node.right.height

            node.height = max(left_height, right_height) + 1
            node.balance_factor = left_height - right_height

            if node.parent is None:
                return

            node = node.parent

    def _balance_tree(self, node: Node):
        if not node.parent:
            return

        curr_node = node.parent

        # verify the tree is balanced at all ancestor nodes
        while True:
            # branch is left heavy
            if curr_node.balance_factor > 1:
                left_node: Node = curr_node.left

                if left_node.left:
                    curr_node = self._right_rotation(curr_node)
                elif left_node.right:
                    curr_node = self._left_right_rotation(curr_node)
            # branch is right heavy
            elif curr_node.balance_factor < -1:
                right_node: Node = curr_node.right

                if right_node.right:
                    curr_node = self._left_rotation(curr_node)
                elif right_node.left:
                    curr_node = self._right_left_rotation(curr_node)

            self._recalculate_height_and_balance_factor(curr_node)

            # reached root
            if curr_node.parent is None:
                return

            curr_node = curr_node.parent

    def _left_rotation(self, z: Node) -> Node:
        y = z.right
        b = y.left

        # replace z with y
        if z.parent and z.parent.left == z:
            z.parent.left = y
        elif z.parent and z.parent.right == z:
            z.parent.right = y
        else:
            self.root = y
        y.parent = z.parent

        # make z left child of y
        y.left = z
        z.parent = y
        z.right = b
        if b:
            b.parent = z

        self._recalculate_height_and_balance_factor(z)
        self._recalculate_height_and_balance_factor(y)

        return y

    def _right_rotation(self, z: Node) -> Node:
        y = z.left
        b = z.right

        # replace z with y
        if z.parent and z.parent.left == z:
            z.parent.left = y
        elif z.parent and z.parent.right == z:
            z.parent.right = y
        else:
            self.root = y
        y.parent = z.parent

        # make z right child of y
        y.right = z
        z.parent = y
        z.left = b
        if b:
            b.parent = z

        self._recalculate_height_and_balance_factor(z)
        self._recalculate_height_and_balance_factor(y)

        return y

    def _left_right_rotation(self, z: Node) -> Node:
        y = z.left

        node = self._left_rotation(y)
        return self._right_rotation(node.parent)

    def _right_left_rotation(self, z: Node) -> Node:
        y = z.right

        node = self._right_rotation(y)
        return self._left_rotation(node.parent)

    def get_shortest_stop(self):
        if self.root is None:
            return

        curr_node = self.root

        # traverse till furthest left node
        while curr_node.left:
            curr_node = curr_node.left

        print(curr_node.stops)

        # stop = None
        # if not curr_node.stops:
        #     stop = curr_node.stops.pop(0)

        # remove node
        if len(curr_node.stops) == 1:
            parent = curr_node.parent
            right_node = curr_node.right

            # deleting root node
            if parent is None:
                self.root = right_node
                # replacing root with right node
                if right_node:
                    right_node.parent = None
                    self._balance_tree(right_node)

            else:
                parent.left = right_node
                if right_node:
                    right_node.parent = parent

                self._balance_tree(parent)

        return curr_node.stops.pop(0)

