print("hello world")

def fib(n):
    if n <= 1:
        return n
    return fib(n-1)
print(fib(10))

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def flatten(root):
    """
    Flattens a Binary Search Tree into a sorted linked list in-place.
    The linked list is constructed by following the right pointers of each node.
    The order of nodes in the linked list will be in ascending order.

    Args:
        root (TreeNode): The root node of the BST to be flattened.

    Returns:
        TreeNode: The head of the flattened linked list.
    """
    if not root:
        return None

    # Initialize a dummy node to simplify the linking process
    dummy = TreeNode(-1)
    prev = dummy

    # Use a stack to perform iterative in-order traversal
    stack = []
    current = root

    while stack or current:
        # Traverse to the leftmost node
        while current:
            stack.append(current)
            current = current.left

        # Pop the top node from the stack
        current = stack.pop()

        # Link the current node to the previous node
        prev.right = current
        prev.left = None  # Ensure left pointer is None
        prev = current

        # Move to the right subtree
        current = current.right

    # The head of the flattened list is dummy.right
    head = dummy.right
    return head

# Example usage:
# Construct a sample BST
#       4
#      / \
#     2   5
#    / \
#   1   3
root = TreeNode(4)
root.left = TreeNode(2)
root.right = TreeNode(5)
root.left.left = TreeNode(1)
root.left.right = TreeNode(3)

# Flatten the BST
flattened_head = flatten(root)
while(flattened_head):
    print(flattened_head.val)
    flattened_head = flattened_head.right