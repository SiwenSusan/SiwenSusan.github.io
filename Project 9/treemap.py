'''
CS 121: PA 6 - Avian Biodiversity Treemap

Siwen Chen

Code for constructing a treemap.
'''

import json
import click
import tree


###############
#             #
#  Your code  #
#             #
###############


class Rectangle:
    '''
    Simple class for representing rectangles.

    Attributes:
        x, y: (float) coordinates of rectangle's origin
        width, height: (float) the rectangle's width and height
        label: (str) text label for the rectangle
        color_code: (tuple) tuple for determining what color the
            rectangle should be
    '''

    def __init__(self, origin, size, label="", color_code=("",)):
        '''
        Constructs a new Rectangle.

        Inputs:
            origin: (pair of float) x and y coordinates of the
                rectangle's origin
            size: (pair of float) the width and height of the rectangle
        '''

        # Validate parameters
        validate_tuple_param(origin, "origin")
        validate_tuple_param(origin, "size")
        assert label is not None, "Rectangle label can't be None"
        assert isinstance(label, str), "Rectangle label must be a string"
        assert color_code is not None, "Rectangle color_code can't be None"
        assert isinstance(color_code, tuple), \
            "Rectangle color_code must be a tuple"

        self.x, self.y = origin
        self.width, self.height = size
        self.label = label
        self.color_code = color_code

    def __str__(self):
        format_string = "RECTANGLE {:.4f} {:.4f} {:.4f} {:.4f} {}"
        return format_string.format(self.x, self.y,
            self.width, self.height, self.label)

    def __repr__(self):
        return str(self)


def compute_rectangles(t, bounding_rec_width=1.0, bounding_rec_height=1.0):
    '''
    Computes the rectangles for drawing a treemap of the provided tree.

    Inputs:
        t: (Tree) a tree
        bounding_rec_width, bounding_rec_height: (float) the width and height
            of the bounding rectangle.

    Returns: a list of Rectangle objects.
    '''

    compute_internal_values(t)
    compute_paths(t)

    total_sum = t.value
    trees = sorted_trees(t.children)
    bounding_rec = Rectangle((0.0, 0.0), (bounding_rec_width, bounding_rec_height))
    rectangles = compute_rectangles_by_trees(trees, bounding_rec, total_sum)

    output_list = []
    for tree, rec in zip(trees, rectangles):
        compute_rectangles_recursively(tree, rec, output_list)

    return output_list
    

def compute_rectangles_by_trees(trees, bounding_rec, total_sum):
    rectangles = []
    while len(trees) > 0:
        if len(trees) == 1:
            bounding_rec.label = trees[0].key
            bounding_rec.color_code = trees[0].path
            rectangles.append(bounding_rec)
            break
        else:
            for i in range(len(trees)):
                if i == 0:
                    row_layout, leftover_rec = compute_row(bounding_rec, trees[:i+1], total_sum)
                    ratio = calculate_max_aspect_ratio(row_layout, bounding_rec.width, bounding_rec.height, total_sum)
                else:
                    new_row_layout, new_leftover_rec = compute_row(bounding_rec, trees[:i+1], total_sum)
                    new_ratio = calculate_max_aspect_ratio(new_row_layout, bounding_rec.width, bounding_rec.height, total_sum)
                    if new_ratio > ratio:
                        break
                    else:
                        ratio = new_ratio
                        row_layout = new_row_layout
                        leftover_rec = new_leftover_rec
            for rec, t in row_layout:
                rec.label = t.key
                rec.color_code = t.path
                total_sum -= t.value
                rectangles.append(rec)
            trees = trees[len(row_layout):]
            bounding_rec = leftover_rec
    return rectangles


def compute_rectangles_recursively(t, rec, output_list):
    if t.num_children() == 0:
        output_list.append(rec)
        return
    trees = sorted_trees(t.children)
    subrectangles = compute_rectangles_by_trees(trees, rec, t.value)
    for subtree, subrec in zip(trees, subrectangles):
        compute_rectangles_recursively(subtree, subrec, output_list)




def calculate_max_aspect_ratio(row_layout, bounding_rec_width, bounding_rec_height, total_sum):
    max_aspect_ratio = None
    for rec, tree in row_layout:
        if max_aspect_ratio == None:
            max_aspect_ratio = max(rec.width / rec.height, rec.height / rec.width)
        else:
            max_aspect_ratio = max(max_aspect_ratio, rec.width / rec.height, rec.height / rec.width)
    return max_aspect_ratio




def compute_internal_values(t):
    '''
    Assign a value to the internal nodes. The value of the leaves should
    already be set. The value of an internal node is the sum of the value
    of its children.

    Inputs:
        t (Tree): a tree

    Returns: The input tree t should be modified so that every internal node's
        value is set to be the sum of the values of its children. The return
        value is the value of the root of t (that is, t.value).
    '''
    if t.num_children() == 0:
        return t.value
    else:
        t.value = sum(compute_internal_values(child) for child in t.children)
        return t.value
    


def compute_paths(t, prefix=()):
    '''
    Assign the path attribute of all nodes. The path attribute of a node
    should be a tuple of strings made up of the keys of the nodes along a
    full path through the tree from the root down to, but not including,
    that node. For example, following the path
        "class Aves" --> "order Passeriformes" --> "family Passerellidae"
    from the root to a node should result in the path atttribute
        ("class Aves", "order Passeriformes")
    being assigned to the node with key "family Passerellidae".
    For the root node, the path attribute should be an empty tuple.

    Inputs:
        t (Tree): a tree
        prefix (tuple of strings): Prefix to add to path

    Returns: Nothing. The input tree t should be modified to contain a path
        attribute for all nodes.
    '''
    t.path = prefix
    for child in t.children:
        child.path = prefix + (t.key,)
        for child_of_child in child.children:
            compute_paths(child_of_child, prefix + (t.key, child.key,))



#############################
#                           #
#  Our code: DO NOT MODIFY  #
#                           #
#############################


def validate_tuple_param(p, name):
    '''
    Validate a tuple parameter.
    '''

    assert isinstance(p, (list, tuple)) and len(p) == 2 \
        and isinstance(p[0], float) and isinstance(p[1], float), \
        name + " parameter to Rectangle must be a tuple or list of two floats"

    errmsg = "Incorrect value for rectangle {}: ({}, {}) "
    assert p[0] >= 0.0 and p[1] >= 0.0, \
        errmsg.format(name, p[0], p[1]) +  "(both values must be >= 0)"


def load_trees(filename):
    '''
    Loads trees from a json file. The json file
    should consist of a dictionary mapping tree
    names to trees represented as lists.

    Input:
        filename: (string) name of the json file.

    Returns: dictionary mapping tree names (strings)
        to Tree instances.
    '''

    with open(filename) as f:
        trees_json = json.load(f)
    return {name: list_to_tree(lst) for name, lst in trees_json.items()}


def list_to_tree(lst):
    '''
    Converts a list to a tree. The first element
    of the list should be a dictionary mapping
    attributes to values. The remaining elements
    of the list are the child subtrees, in the
    same format.

    Input:
        lst: list representing a tree.

    Returns: a Tree instance.
    '''

    root = lst[0]
    children = lst[1:]
    t = tree.Tree(fancy_get(root, 'key'), fancy_get(root, 'value'))
    for attrname in root:
        attrvalue = fancy_get(root, attrname)
        if attrname not in ['key', 'value']:
            setattr(t, attrname, attrvalue)
    for child_list in children:
        t.add_child(list_to_tree(child_list))
    return t


def fancy_get(d, key, default=None):
    '''
    Gets a value from a dictionary, but converts a list to a tuple.
    '''
    val = d.get(key, default)
    if isinstance(val, list):
        return tuple(val)

    return val


def sorted_trees(tree_list):
    '''
    Sort a list of Tree instances by the value of their roots in descending
    order. Ties are broken by the key of the root, in (forward) alphabetical
    order. Returns a new sorted list without modifying the input list.

    Inputs:
        tree_list: list of Tree instances, each with an integer value.

    Returns: list of Tree instances, sorted.
    '''

    return sorted(tree_list, key=lambda t: (-t.value, t.key))


def compute_row(bounding_rec, row_data, total_sum):
    '''
    Lay out the given data points as rectangles in one row of a
    treemap. The row will be against the left or top edge of the
    bounding rectangle, depending on whether the rectangle is at least
    as wide as it is tall.

    Inputs:
        bounding_rec: (Rectangle) the bounding rectangle
        row_data: (list of Tree) the list of data points that should be
            included in this row.
        total_sum: (integer) the total value of all the rectangles that
            will eventually fill the bounding rectangle (not just those
            in this row).

    Returns: a tuple (row_layout, leftover_rec), where
        row_layout: list of pairs (rec, t), where rec is a Rectangle, and
            t is the Tree that Rectangle corresponds to, and
        leftover_rec: a Rectangle representing the leftover space in the
            bounding rectangle that was not used by this row.
    '''

    if bounding_rec.width >= bounding_rec.height:
        return __compute_row_wide(bounding_rec, row_data, total_sum)
    else:
        row_layout_t, leftover_rec_t = __compute_row_wide(
            __transpose_rectangle(bounding_rec), row_data, total_sum)
        row_layout = [(__transpose_rectangle(rec), tr)
            for rec, tr in row_layout_t]
        leftover_rec = __transpose_rectangle(leftover_rec_t)
        return row_layout, leftover_rec


def __transpose_rectangle(rec):
    '''
    Returns a new rectangle that is the transpose of the input: The x and y
    attributes are switched, as are width and height. The label and
    color_code attributes are preserved.

    Input:
        rec: (Rectangle)

    Returns: (Rectangle) transpose of rec.
    '''

    return Rectangle((rec.y, rec.x), (rec.height, rec.width),
        rec.label, rec.color_code)


def __compute_row_wide(bounding_rec, row_data, total_sum):
    '''
    Helper function for compute_row. Serves the same purpose as compute_row,
    but only when the bounding rectangle is at least as wide as it is tall.

    Inputs: Same as compute_row, except that bounding_rec must have a width
        greater than or equal to its height.
    Returns: Same as compute_row.
    '''

    assert bounding_rec.width >= bounding_rec.height
    row_sum = sum(t.value for t in row_data)
    row_width = bounding_rec.width * row_sum / total_sum
    row_layout = []
    y = bounding_rec.y
    for t in row_data:
        height = bounding_rec.height * t.value / row_sum
        rec = Rectangle((bounding_rec.x, y),
                        (row_width, height))
        if rec.width > 0 and rec.height > 0:
            row_layout.append((rec, t))
        y += height
    leftover = Rectangle((bounding_rec.x + row_width, bounding_rec.y),
                         (bounding_rec.width - row_width, bounding_rec.height))

    return row_layout, leftover


@click.command(name="treemap")
@click.argument('tree_file', type=click.Path(exists=True))
@click.argument('key', type=str)
@click.option('--output', '-o', type=str)
def cmd(tree_file, key, output):
    import drawing

    data = load_trees(tree_file)

    data_tree = data[key]

    compute_internal_values(data_tree)

    compute_paths(data_tree)

    rectangles = compute_rectangles(data_tree)

    if output == "-":
        for rect in rectangles:
            print(rect)
    else:
        drawing.draw_rectangles(rectangles, output)

if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter
