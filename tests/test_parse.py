from Scalpels.LGSgfParser import LGSgfParser
from Scalpels.util import BlackMove, WhiteMove, WhiteMoveWithComment


def test_parse_LGSgf_ReturnsCorrectMoveList():
    sample_sgf = "(;FF[4]EV[connect6.ch.26.1.1]PB[Phoenix]PW[Lomaben]SO[http://www.littlegolem.com];B[j10];W[j9l11];" \
                 "B[k9l8];W[k10i11])"

    actual = LGSgfParser.parse(sample_sgf, "SAMPLE")
    expected = [BlackMove(9, 9),
                WhiteMove(9, 8),
                WhiteMove(11, 10),
                BlackMove(10, 8),
                BlackMove(11, 7),
                WhiteMove(10, 9),
                WhiteMoveWithComment(8, 10, comment="SAMPLE"), ]

    assert actual == expected
