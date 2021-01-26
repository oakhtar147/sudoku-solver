##############################################################
#                    ENCODING THE BOARD                      #
##############################################################


# Creating labels for the boxes
rows = 'ABCDEFGHI'
cols = '123456789'

# The below function will return the list formed by all the possible
# concatenations of a letter s in string a with a letter t in string b.
def cross(a,b):
    boxes = []
    for s in a:
        for t in b:
            boxes.append(s+t)

    return boxes

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rows[x:x+3], cols[y:y+3]) for x in range(0,9,3) for y in range(0,9,3)]

unitList = row_units + column_units + square_units

def grid2values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """

    sodukoDict = {}

    for i in range(len(grid)):
        if grid[i] != '.':
            sodukoDict[boxes[i]] = grid[i]
        else:
            sodukoDict[boxes[i]] = '123456789'

    return sodukoDict

##############################################################
#                       HELPER FUNCTIONS                     #
##############################################################

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    if values:
        width = 1+max(len(values[s]) for s in boxes)
        line = '+'.join(['-'*(width*3)]*3)
        for r in rows:
            print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                          for c in cols))
            if r in 'CF': print(line)
        return

def print_soduko(grid):
    """Prints soduko puzzle"""
    display(dict(zip(boxes, grid)))



##############################################################
#                    NAKED TWINS                             #
##############################################################


def intersection(A,B):
    '''Takes two arrays and returns the common elements in both'''
    return [value for value in A if value in B]


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers
    """
    for boxA in values.keys():
        if len(values[boxA]) == 2:
            for boxB in findPeers(boxA):
                if values[boxA] == values[boxB]:
                    for peer in intersection(findPeers(boxA), findPeers(boxB)):
                        for digit in values[boxA]:
                            values[peer] = values[peer].replace(digit, '')
                            # values = assign_value(values, peer, values[peer].replace(digit, ''))

    return values

##############################################################
#                        ELIMINATION                         #
##############################################################


def findPeers(pos):
    """Returns all peers of a certain position

    Args:
        Soduko position
    Returns:
        An array of positions of all the peers (20 peers)
    """

    # Identify the units in which pos is present
    for row_unit in row_units:
        if pos in row_unit:
            row = row_unit
            break

    for col_unit in column_units:
        if pos in col_unit:
            col = col_unit
            break

    for square_unit in square_units:
        if pos in square_unit:
            square = square_unit


    peers = list(set(row + col + square))
    peers.remove(pos)
    peers = sorted(peers)

    return peers

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]

    for boxPos in solved_values:
        boxVal = values[boxPos]

        # Find all peers for the position
        peerPositions = findPeers(boxPos)

        # Perform elimination for each of the peers
        for peerPos in peerPositions:
            values[peerPos] = values[peerPos].replace(boxVal, '')
            # values = assign_value(values, peerPos,values[peerPos].replace(boxVal, ''))

    return values

##############################################################
#                        ONLY CHOICE                         #
##############################################################


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitList:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
                # values = assign_value(values, dplaces[0], digit)
    return values

##############################################################
#              APPLYING STRATEGIES ITERATIVELY               #
##############################################################


def reduce_puzzle(values):
    """
    Iterate eliminate(), naked_twins() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use Naked Twins Strategy
        values = naked_twins(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

##############################################################
#                   DEPTH FIRST SEARCH                       #
##############################################################


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    # Failure
    if not values:
        return False

    # Success
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!

    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_boxes = [box for box in values.keys() if len(values[box]) > 1]
    s = unsolved_boxes[0]

    for box in unsolved_boxes:
        if values[box] < values[s]:
            s = box

    # n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        # new_board = assign_value(new_board, easiest_square_coor, possible_value)
        new_sudoku = values.copy()
        new_sudoku[s] = value
        # new_sudoku = assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '123......456......789.......................................123......456......789'
    print_soduko(diag_sudoku_grid)
    print('\n')
    result = solve(diag_sudoku_grid)

    display(result)