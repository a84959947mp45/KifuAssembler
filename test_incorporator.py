from Move import BlackMove, WhiteMove
from incorporator import Incorporator


def test_toTuple_ValidMoves_ReturnCorrectTree():
    moves = (BlackMove(10, 10),
             WhiteMove(0, 0),
             BlackMove(10, 11))

    incorporator = Incorporator(moves)

    actual = incorporator.to_tuple()
    expected = ("Root",
                BlackMove(10, 10),
                WhiteMove(0, 0),
                BlackMove(10, 11))

    assert actual == expected


# def test_incorporate_ValidMoves_ReturnCorrectTree():
#     moves1 = (BlackMove(10, 10),
#               WhiteMove(0, 0),
#               BlackMove(10, 11))
#     moves2 = (BlackMove(10, 10),
#               WhiteMove(1, 1),
#               BlackMove(10, 11))
#
#     incorporator = Incorporator(moves1)
#     incorporator.incorporate(moves2)
#
#     actual = incorporator.to_tuple()
#     expected = (BlackMove(10, 10),
#                 (WhiteMove(0, 0), BlackMove(10, 11)),
#                 (WhiteMove(1, 1), BlackMove(10, 11)),)
#
#     assert actual == expected
