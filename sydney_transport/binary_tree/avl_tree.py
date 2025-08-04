from datetime import timedelta, datetime
import sys

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

    def insert(self, stop: Stop, travel_duration: timedelta):
        """
        Inserts a Stop into the AVL Tree, then recalculates the height and
        balance factors before rebalancing the AVL Tree.
        """
        new_node = Node(stop, travel_duration)

        # empty tree
        if self.root is None:
            self.root = new_node
            return

        curr_node: Node = self.root

        # loop through nodes till a valid insertion location is found
        while True:
            # insert left
            if travel_duration < curr_node.travel_duration and curr_node.left is None:
                curr_node.left = new_node
                break
            # insert right
            if travel_duration > curr_node.travel_duration and curr_node.right is None:
                curr_node.right = new_node
                break
            # insert in current node
            if travel_duration == curr_node.travel_duration:
                curr_node.stops.append(stop)
                break

            # traverse left branch
            if travel_duration < curr_node.travel_duration:
                curr_node = curr_node.left
            # traverse right branch
            elif travel_duration > curr_node.travel_duration:
                curr_node = curr_node.right

        self._check_avl_quality(allow_rotations=True)

    def _check_avl_quality(self, allow_rotations: bool, node: Node = None) -> int:
        # tree is empty
        if self.root is None:
            print("Error: avl_tree.py: tree is empty")
            sys.exit(0)

        # starting from root
        if node is None:
            node = self.root

        # node is a leaf
        if node.left is None and node.right is None:
            node.height = 0
            node.balance_factor = 0
            return 0

        left_height = 0
        right_height = 0

        # node has left branch
        if node.left is not None:
            left_height = self._check_avl_quality(True, node.left) + 1

            # left subbranch is unbalanced
            if allow_rotations and node.left.balance_factor not in range(-1, 2):
                node.left = self._perform_rotation(node.left)
                left_height = self._check_avl_quality(False, node.left) + 1

        # node has right branch
        if node.right is not None:
            right_height = self._check_avl_quality(True, node.right) + 1

            # right subbranch is unbalanced
            if allow_rotations and node.right.balance_factor not in range(-1, 2):
                node.right = self._perform_rotation(node.right)
                right_height = self._check_avl_quality(False, node.right) + 1

        # set node values
        node.height = max(left_height, right_height)
        node.balance_factor = left_height - right_height

        # root is unbalanced
        if allow_rotations and self.root == node and node.balance_factor not in range(-1, 2):
            self._perform_rotation(node)
            self._check_avl_quality(allow_rotations=False)

        return node.height

    def _perform_rotation(self, node: Node):
        """
        Performs a rotation on a subbranch.
        :param node: Root of the unbalanced subbranch.
        """
        # branch if left heavy
        if node.balance_factor > 1:
            left_node: Node = node.left

            if left_node.left:
                return self._right_rotation(node)
            elif left_node.right:
                return self._left_right_rotation(node)
        # branch is right heavy
        elif node.balance_factor < -1:
            right_node: Node = node.right

            if right_node.right:
                return self._left_rotation(node)
            elif right_node.left:
                return self._right_left_rotation(node)


    def _left_rotation(self, node: Node):
        """
        Performs a left rotation on the root of the unbalanced subbranch.
        Returns the new subbranch root.
        """
        right_child = node.right

        # maintain root
        if self.root == node:
            self.root = right_child

        node.right = right_child.left
        right_child.left = node

        return right_child
        # TODO: Double check if the avl_quality should be checked again after _check_avl_quality()
        # self._check_avl_quality(right_child)

    def _right_rotation(self, node: Node):
        """
        Performs a right rotation on the root of the unbalanced subbranch.
        Returns the new subbranch root.
        """
        left_child = node.left

        # maintain root
        if self.root == node:
            self.root = left_child

        node.left = left_child.right
        left_child.right = node

        return left_child
        # self._check_avl_quality(left_child)

    def _left_right_rotation(self, node: Node):
        """
        Performs a left-right rotation on the root of the unbalanced subbranch.
        Returns the new subbranch root.
        """
        node.left = self._left_rotation(node.left)
        return self._right_rotation(node)

    def _right_left_rotation(self, node: Node):
        """
        Performs a right-left rotation on the root of the unbalanced subbranch.
        Returns the new subbranch root.
        """
        node.right = self._right_rotation(node.right)
        return self._left_rotation(node)

    def remove_closest_stop(self):
        """
        Removes the closest Stop.
        If the Stop is the last one in the Node it will remove the Node and
        rebalance the AVL Tree.
        """
        # tree is empty
        if self.root is None:
            print("Error: avl_tree: remove_closest_stop(): tree is empty")
            sys.exit(0)

        current_node: Node = self.root
        node_above_current = None

        # traverse till furthest left node
        while current_node.left:
            node_above_current = current_node
            current_node = current_node.left

        # remove node
        if len(current_node.stops) == 1:
            # deleting root node
            if current_node == self.root:
                self.root = None

                # replacing root with right node
                if current_node.right:
                    self.root = current_node.right

            elif node_above_current is not None:
                node_above_current.left = current_node.right

        return current_node.stops.pop(0)



































