from typing import TextIO

from anytree import AnyNode, PreOrderIter

from KifuAssembler.src.utils import KifuParser, Root, WhiteMove, BlackMove, gogui_style_str, \
    all_possible_actions, GAME_CONFIG
import copy


def detailed_str(a_node: AnyNode):
    result = str(a_node.data)
    result += "C["
    if a_node.visit_cnt >= 2:
        result += f"Visit Count = {a_node.visit_cnt}\n"
    result += f"BWin count  = {a_node.bwin}\n"
    result += f"WWin count  = {a_node.wwin}\n"
    result += f"Draw count  = {a_node.draw}\n"
    if isinstance(a_node.data, BlackMove):
        win_rate = format(
            100 * ((a_node.bwin + a_node.draw / 2) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        Black_win_rate = format(
            100 * ((a_node.bwin) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        Draw_rate = format(
            100 * ((a_node.draw) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        result += f"WinRate     = {win_rate}%\n"
        result += f"BlackWinRate     = {Black_win_rate}%\n"
        result += f"DrawWinRate     = {Draw_rate }%\n"

    elif isinstance(a_node.data, WhiteMove):
        win_rate = format(
            100 * ((a_node.wwin + a_node.draw / 2) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        White_win_rate = format(
            100 * ((a_node.wwin) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        Draw_rate = format(
            100 * ((a_node.draw) / (
                    a_node.bwin + a_node.wwin + a_node.draw)),
            '3.2f'
        )
        result += f"WinRate     = {win_rate}%\n"
        result += f"WhiteWinRate     = {White_win_rate}%\n"
        result += f"DrawWinRate     = {Draw_rate }%\n"

    if a_node.urls and a_node.is_terminate_node:
        result += f"Game urls   = "
        result += ", ".join(a_node.urls)
        result += "\n"

    if a_node.is_a_chosen_opening:
        result += f"Chosen opening!\n"

    result += "]"
    return result


def rearrange(moves):
    r"""
    Rearrange a sequence of moves, so that moves with smaller idx will always appear before larger one.

    This is useful to merge moves in connect6, where two same-color moves with different order are consider the same.

    # WhiteMove(9, 8) has bigger index than WhiteMove(8, 8), so they are swapped.
    >>> rearrange( [BlackMove(9, 9), WhiteMove(9, 8), WhiteMove(8, 8)] )
    [BlackMove(x=9, y=9), WhiteMove(x=8, y=8), WhiteMove(x=9, y=8)]
    >>> rearrange( [BlackMove(9, 9), WhiteMove(8, 8), WhiteMove(9, 8)] )
    [BlackMove(x=9, y=9), WhiteMove(x=8, y=8), WhiteMove(x=9, y=8)]
    >>> rearrange( [BlackMove(9, 9), WhiteMove(1, 1), WhiteMove(8, 8)] )
    [BlackMove(x=9, y=9), WhiteMove(x=1, y=1), WhiteMove(x=8, y=8)]
    """
    result = []
    for mv in moves:
        if len(result) >= 1 and type(result[-1]) == type(mv):
            if result[-1] > mv:
                result[-1], mv = mv, result[-1]
        result.append(mv)
    return result


class Assembler:
    r"""
    An assembler that can merge various game moves into a tree-like structure.

    This class is used by json_to_tree.py for assembling different kifus.
    """

    def __init__(self, moves=None, url="_sample_url_", *, game_results="Draw", merge_symmetric_moves=False):
        self.root = AnyNode(
            data=Root(),
            parent=None,
            visit_cnt=0,
            urls=[],
            bwin=0,
            wwin=0,
            draw=0,
            is_a_chosen_opening=False,
            is_terminate_node=False
        )

        self.merge_symmetric_moves = merge_symmetric_moves

        if moves:
            self.assemble(moves, url, game_results)

    def assemble(self, moves: list, url="_sample_url_", game_results="Draw"):
        if self.merge_symmetric_moves:
            self._symmetrical_assemble(moves, url, game_results)
        else:
            self._normal_assemble(moves, url, game_results)

    def _normal_assemble(self, moves: list, url="_sample_url_", game_results="Draw"):
        # Start from root node
        current_node = self.root

        while True:
            current_node.visit_cnt += 1

            if len(moves) == 0:
                current_node.urls.append(url)
                current_node.is_terminate_node = True

            if game_results == "BWin":
                current_node.bwin += 1
            elif game_results == "WWin":
                current_node.wwin += 1
            elif game_results == "Draw":
                current_node.draw += 1

            if not moves:
                break

            current_mv = moves.pop(0)
            # Find the child from current_node which's content is identical to current_mv
            results = [c for c in current_node.children if c.data == current_mv]

            if results:
                # If such child exists, replace `current_node` to that child
                # This makes us walk to the deeper tree node to search for the first never-seen moves
                current_node = results[0]
            else:
                # Otherwise, attach a new node to the tree
                new_node = AnyNode(
                    data=current_mv,
                    parent=current_node,
                    visit_cnt=0,
                    urls=[],
                    bwin=0,
                    wwin=0,
                    draw=0,
                    is_a_chosen_opening=False,
                    is_terminate_node=False
                )
                current_node = new_node

    def _symmetrical_assemble(self, moves: list, url="_sample_url_", game_results="Draw"):
        def find_game_turns_that_is_not_present_on_the_tree(mvs):
            current_node = self.root
            idx, turns = 0, 0

            while idx < len(mvs):
                children = [c for c in current_node.children if c.data == mvs[idx]]
                if children:
                    chosen_child = min(children)
                    idx += 1
                    if (idx - GAME_CONFIG.p) % GAME_CONFIG.q == 0:
                        turns += 1
                    current_node = chosen_child
                else:
                    break

            return turns

        if len(moves) == 0:
            return

        symmetric_moves_lists = []
        for action in all_possible_actions():
            sym_mvs = rearrange([action(mv) for mv in moves])
            symmetric_moves_lists.append(sym_mvs)

        mvs = min(symmetric_moves_lists, key=lambda mvs: mvs)

        largest_depth = find_game_turns_that_is_not_present_on_the_tree(mvs)

        # Assert that the chosen move list has the largest depth
        assert all([find_game_turns_that_is_not_present_on_the_tree(moves_list) <= largest_depth for moves_list in
                    symmetric_moves_lists])

        self._normal_assemble(mvs, url, game_results)

    def top_n_moves(self, amount: int):
        def dfs(current_node, depth, sgf: str):
            sgf += ";" + str(current_node.data)
            valid_children = [child for child in current_node.children if child.visit_cnt >= visit_cnt_threshold]
            valid_children = sorted(valid_children, key=lambda node: node.visit_cnt)

            original_length = len(result)

            for child in valid_children:
                dfs(child, depth + 1, sgf)

            if sgf and is_end_of_turn(depth):
                if original_length == len(result):
                    result.append(sgf)
                    result_nodes.append(current_node)

                elif original_length + 1 == len(result):
                    result.pop(-1)
                    result.append(sgf)
                    result_nodes.pop(-1)
                    result_nodes.append(current_node)

        if amount == 0:
            return []

        for visit_cnt_threshold in range(self.root.visit_cnt, 0, -1):
            result = []
            result_nodes = []

            dfs(self.root, depth=0, sgf="")

            print(f"Current threshold is {visit_cnt_threshold : >5}, result has length {len(result): >5} ")
            if len(result) >= amount or visit_cnt_threshold == 0:
                for node in result_nodes[:amount:]:
                    node.is_a_chosen_opening = True
                return result[:amount:]


def to_tuple(an_Assembler: Assembler):
    """Returns a pre-order tree traversal node sequence"""
    return copy.deepcopy(tuple(node.data for node in PreOrderIter(an_Assembler.root)))


def is_end_of_turn(d):
    if d == 0 or d == GAME_CONFIG.p:
        return True
    elif d > GAME_CONFIG.p and (d - GAME_CONFIG.p) % GAME_CONFIG.q == 0:
        return True
    else:
        return False


def dump_to(an_Assembler: Assembler, file: TextIO, *, editor_style):
    """Dump the tree structure inside an assembler to a file (in sgf format)."""

    def simple_tree_traverse(current_node, file: TextIO):
        file.write(detailed_str(current_node))

        for child in current_node.children:
            if len(current_node.children) >= 2:
                file.write("(;")
            else:
                file.write(";")

            simple_tree_traverse(child, file)

            if len(current_node.children) >= 2:
                file.write(")")


    def editor_style_tree_traverse(current_node: AnyNode, depth: int, branch_flag: bool, sgf: str, file: TextIO):
        depth += 1
        if is_end_of_turn(depth):
            for child in current_node.children:
                if branch_flag: file.write("(")
                file.write(f"{sgf};{detailed_str(child)}")
                editor_style_tree_traverse(child, depth, len(child.children) > 1, "", file)
                if branch_flag: file.write(")")

        else:
            for child in current_node.children:
                child_branch_flag = branch_flag or len(child.children) > 1
                editor_style_tree_traverse(child, depth, child_branch_flag, sgf + ";" + detailed_str(child), file)

    file.write("(;GM[511]")
    if editor_style:
        editor_style_tree_traverse(an_Assembler.root, 0, len(an_Assembler.root.children) > 1, "", file)
    else:
        simple_tree_traverse(an_Assembler.root, file)
    file.write(")")
    file.write(detailed_str(an_Assembler.root))


def to_GoGui_sgf(a_str):
    moves = [gogui_style_str(mv) for mv in KifuParser.parse(a_str)][1:]
    return "(;FF[4]CA[UTF-8]AP[GoGui:1.5.1];" + ";".join(moves) + ")"


def to_Pure_sgf(a_str):
    return "".join([";" + str(mv) for mv in KifuParser.parse(a_str)])
