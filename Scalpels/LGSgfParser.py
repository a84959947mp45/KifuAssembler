from itertools import product

from .util import BlackMove, WhiteMove, BlackMoveWithComment, WhiteMoveWithComment


class LGSgfParser:
    """
    Little Golem Sgf parser that can convert a sgf into a sequence of moves.
    """
    table = {}

    for i, j in product("abcdefghijklmnopqrs", range(1, 20)):
        table[f"{i}{j}"] = ("abcdefghijklmnopqrs".index(i), j - 1)

    for i, j, i2, j2 in product("abcdefghijklmnopqrs", range(1, 20), "abcdefghijklmnopqrs", range(1, 20)):
        table[f"{i}{j}{i2}{j2}"] = \
            ("abcdefghijklmnopqrs".index(i), j - 1, "abcdefghijklmnopqrs".index(i2), j2 - 1)

    @staticmethod
    def parse(lg_sgf: str, url=None):
        """
        :param lg_sgf: The Little Golem Sgf string to parse
        :param url: Attach this url as a comment to the last move if given
        """

        # Split lg_sgf by ';' and discard the element if it is empty.
        moves = [e for e in lg_sgf[1:-1].split(';') if e]
        moves.pop(0)

        result = []

        for move in moves:
            role = move[0]
            if role == 'B':
                if len(LGSgfParser.table[move[2:-1]]) == 2:
                    i, j = LGSgfParser.table[move[2:-1]]
                    result.append(BlackMove(i, j))
                elif len(LGSgfParser.table[move[2:-1]]) == 4:
                    i1, j1, i2, j2 = LGSgfParser.table[move[2:-1]]
                    result.append(BlackMove(i1, j1))
                    result.append(BlackMove(i2, j2))

            elif role == 'W':
                if len(LGSgfParser.table[move[2:-1]]) == 2:
                    i, j = LGSgfParser.table[move[2:-1]]
                    result.append(WhiteMove(i, j))
                elif len(LGSgfParser.table[move[2:-1]]) == 4:
                    i1, j1, i2, j2 = LGSgfParser.table[move[2:-1]]
                    result.append(WhiteMove(i1, j1))
                    result.append(WhiteMove(i2, j2))

        if url:
            if isinstance(result[-1], BlackMove):
                result[-1] = BlackMoveWithComment(result[-1].i, result[-1].j, comment=url)
            elif isinstance(result[-1], WhiteMove):
                result[-1] = WhiteMoveWithComment(result[-1].i, result[-1].j, comment=url)

        return result
