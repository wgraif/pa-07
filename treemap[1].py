# CS121: PA 7 - Diversity Treemap
# Name: WILLIAM GRAIF
# Code for constructing a treemap.

import argparse
import pandas as pd
import sys
import tree
import drawing
import click

###############
#             #
#  Your code  #
#             #
###############



def helper(df, column):
    new_df = df.groupby([column])["count"].sum().to_dict()
    for name in new_df:
        print(name, " : ", new_df[name])


def load_diversity_data(filename, debug=False):
    '''
    Load Silicon Valley diversity data and print summary

    Inputs:
        filename: (string) the name pf the file with the data

    Returns: a pandas dataframe
    '''
    df = pd.read_csv(filename)

    if debug:
        print(df["company"].unique(), len(df["company"].unique()))
        print(df["count"].sum())
        helper(df, "gender")
        helper(df, "race")
        helper(df, "job_category")

    return df


def compute_internal_counts(t):
    '''
    Assign a count to the interior nodes.  The count of the leaves
    should already be set.  The count of an internal node is the sum
    of the counts of its children.

    Inputs:
        t (Tree): a tree

    Returns:
        The input tree t should be modified so that every internal node's
        count is set to be the sum of the counts of its children.

        The return value will be:
        - If the tree has no children: the value of the count attribute
        - If the tree has children: the sum of the counts of the children
    '''

    if t.count is None:
        t.count = 0

    if len(t.children) == 0:
        return t.count

    else:
        for child in t.children:
            compute_internal_counts(child)
            t.count += child.count

    return t.count


def compute_verbose_labels(t, prefix=None):
    '''
    Assign a verbose label to non-root nodes. Verbose labels contain the 
    full path to that node through the tree. For example, following the 
    path "Google" --> "female" --> "white" should create the verbose label 
    "Google: female: white". For the root node, the verbose label should be
    an empty string ("").

    Inputs:
        t (Tree): a tree
        prefix (string): Prefix to add to verbose label

    Outputs:
        Nothing. The input tree t should be modified to contain
            verbose labels for all nodes
    '''

    if t.verbose_label is None:
        t.verbose_label = t.label

    if len(t.children) == 0:
        return None

    for child in t.children:
        if t.label == "":
            t.verbose_label = ""
        else:
            child.verbose_label = str(t.verbose_label + ": " + child.label)

        compute_verbose_labels(child)

    return None


def prune_tree(original_sub_tree, values_to_discard):
    '''
    Returns a tree with any node whose label is in the list values_to_discard
    (and thus all of its children) pruned. This function should return a copy
    of the original tree and should not destructively modify the original tree.
    The pruning step must be recursive.

    Inputs:
        t (Tree): a tree
        values_to_discard (list of strings): A list of strings specifying the
                  labels of nodes to discard

    Returns: a new Tree object representing the pruned tree
    '''
    
    nodes = []
    if original_sub_tree.num_children() == 0:
        return tree.Tree(original_sub_tree.label, original_sub_tree.count)

    else:
        for child in original_sub_tree.children:
            if child.label not in values_to_discard:
            	nodes.append(prune_tree(child, values_to_discard))
        
        return tree.Tree(original_sub_tree.label, original_sub_tree.count,
            nodes)


def validate_tuple_param(p, name):
    assert isinstance(p, (list, tuple)) and len(p) == 2 \
        and isinstance(p[0], float) and isinstance(p[1], float), \
        name + " parameter to Rectangle must be a tuple or list of two floats"

    assert p[0] >= 0.0 and p[1] >= 0.0, \
        "Incorrect value for rectangle {}: ({}, {}) ".format(name, p[0], p[1]) + \
        "(both values must be >= 0)"


class Rectangle:
    '''
    Simple class for representing rectangles
    '''
    def __init__(self, origin, size, label, verbose_label):
        # Validate parameters
        validate_tuple_param(origin, "origin")
        validate_tuple_param(origin, "size")
        assert label is not None, "Rectangle label can't be None"
        assert isinstance(label, str), "Rectangle label must be a string"
        assert verbose_label is not None, "Rectangle verbose_label can't be None"
        assert isinstance(verbose_label, str), "Rectangle verbose_label must be a string"

        self.x, self.y = origin
        self.width, self.height = size
        self.label = label
        self.verbose_label = verbose_label

    def __str__(self):
        if self.verbose_label is None:
            label = self.label
        else:
            label = self.verbose_label

        return "RECTANGLE {:.4f} {:.4f} {:.4f} {:.4f} {}".format(self.x, self.y,
                                                                 self.width, self.height,
                                                                 label)

    def __repr__(self):
        return str(self)


def get_prop(t, x0, y0, width, height, increment = True):
    '''
    Inputs: a tree, starting point for a rectangle, its width and height,
            and a boolean value for whether we are editing width or height.

    Returns: a list of rectangle objects.

    This is a helper function for compute_rectangles. It uses recursion to
    get the proportions, which are used to make the list of rectangle objects.
    This function is then called in compute_rectangles.
    '''

    list_prop = []
    if t.num_children() == 0:
        list_prop.append(Rectangle((x0, y0), (width, height), t.label,
            t.verbose_label))

    else:

        for child in t.children:
            if increment:
                if t.count == 0:
                    final_width = 0
                else:
                    final_width = (child.count / t.count) * width

                list_prop += get_prop(child, x0, y0, final_width, height,
                    False)
                x0 += final_width

            else:
                if t.count == 0:
                    final_height = 0
                else:
                    final_height = (child.count / t.count) * (height)

                list_prop += get_prop(child, x0, y0, width, final_height,
                    True)
                y0 += final_height

    return list_prop


def compute_rectangles(t, bounding_rec_height=1.0, bounding_rec_width=1.0):
    '''
    Computes the rectangles for drawing a treemap of the provided tree

    Inputs:
        t (Tree): a tree
        bounding_rec_height, bounding_rec_width (floats): the size of
           the bounding rectangle.

    Returns: a list of Rectangle objects
    '''

    compute_internal_counts(t)
    compute_verbose_labels(t)

    return get_prop(t, 0., 0., bounding_rec_width, bounding_rec_height)


#############################
#                           #
#  Our code: DO NOT MODIFY  #
#                           #
#############################

@click.command(name="treemap")
@click.argument('diversity_file', type=click.Path(exists=True))
@click.option('--categories', '-c', type=str)
@click.option('--prune', '-p', type=str)
@click.option('--output', '-o', type=str)
def cmd(diversity_file, categories, prune, output):

    data = load_diversity_data(diversity_file)

    if categories is not None:
        categories = categories.split(",")

    if prune is not None:
        prune = prune.split(",")

    data_tree = tree.data_to_tree(data, categories)

    compute_internal_counts(data_tree)

    compute_verbose_labels(data_tree)

    if prune is not None:
        data_tree = prune_tree(data_tree, prune)

    rectangles = compute_rectangles(data_tree)

    if output == "-":
        for rect in rectangles:
            print(rect)
    else:
        drawing.draw_rectangles(rectangles, output)

if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter