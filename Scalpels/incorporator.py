from anytree import AnyNode, RenderTree, PreOrderIter

from Scalpels.util import Root, WhiteMove, BlackMove


class Incorporator:
    """
    An incorporator that can merge various game moves into a tree-like structure.

    >>> from Scalpels.util import BlackMove, WhiteMove, Root
    >>> moves = [BlackMove(10, 10), WhiteMove(0, 0), BlackMove(10, 11)]
    >>> incorporator = Incorporator(moves)
    >>> incorporator.print_tree()
    <BLANKLINE>
    └── B[KK]
        └── W[AA]
            └── B[KL]


    >>> moves2 = [BlackMove(10, 10), WhiteMove(1, 1), BlackMove(10, 11)]
    >>> incorporator.incorporate(moves2)
    >>> incorporator.print_tree()
    <BLANKLINE>
    └── B[KK]
        ├── W[AA]
        │   └── B[KL]
        └── W[BB]
            └── B[KL]
    """

    def __init__(self, moves=None):
        self.root = AnyNode(data=Root(), visit_cnt=1)
        if moves:
            self.incorporate(moves)

    def incorporate(self, moves: list):
        """
        This algorithm incorporate moves into the tree.
        It searches for the first move that has never been seen on the tree,
        and attach the remaining moves to the tree.
        """

        current_node = self.root

        while moves:
            current_mv = moves.pop(0)

            # Get the specific child from current_node which it's content is identical to current_mv
            result = [c for c in current_node.children if c.data == current_mv]

            if result:
                # If such child exists, replace `current_node` to that child
                # This makes us walk to the deeper tree node to search for the first never-seen moves
                current_node = result[0]
                current_node.visit_cnt += 1
                continue

            else:
                # Otherwise, attach the remaining moves into a new branch in the tree
                parent = AnyNode(data=current_mv, parent=current_node, visit_cnt=1)
                for mv in moves:
                    parent = AnyNode(data=mv, parent=parent, visit_cnt=1)
                break

    def to_tuple(self):
        return tuple(node.data for node in PreOrderIter(self.root))

    def to_sgf(self):
        """
        Convert the internal tree into a sgf string.

        :return: the sgf string
        """

        def depth_first_traversal(current_node, result):
            result += str(current_node.data)
            if current_node.visit_cnt >= 2:
                result += f"C[Visit Count := {current_node.visit_cnt}\n]"
            for child in current_node.children:
                if len(current_node.children) >= 2:
                    result += "(;"
                else:
                    result += ";"
                result = depth_first_traversal(child, result)
                if len(current_node.children) >= 2:
                    result += ")"
            return result

        return depth_first_traversal(self.root, "")

    def print_tree(self):
        for pre, _, node in RenderTree(self.root):
            print(f"{pre}{node.data}")
