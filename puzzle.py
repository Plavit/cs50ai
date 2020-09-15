from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Knowledge about rules of the game - exclusive or that each person is either a knight or a knave
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),

    # Knowledge about input statements
    Biconditional(And(AKnave, AKnight), AKnight)

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Knowledge about rules of the game - exclusive or that each person is either a knight or a knave
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),
    Or(BKnave, BKnight),
    Not(And(BKnave, BKnight)),

    # Knowledge about input statements
    Biconditional(And(AKnave, BKnave), AKnight)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Knowledge about rules of the game - exclusive or that each person is either a knight or a knave
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),
    Or(BKnave, BKnight),
    Not(And(BKnave, BKnight)),

    # Knowledge about input statements
    Biconditional(Or(And(BKnight, AKnight), And(BKnave, AKnave)), AKnight),
    Biconditional(And(Or(BKnight, AKnight), Not(And(BKnight, AKnight))), BKnight)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Knowledge about rules of the game - exclusive or that each person is either a knight or a knave
    Or(AKnave, AKnight),
    Not(And(AKnave, AKnight)),
    Or(BKnave, BKnight),
    Not(And(BKnave, BKnight)),
    Or(CKnave, CKnight),
    Not(And(CKnave, CKnight)),

    # Knowledge about input statements
    Or(Biconditional(AKnight, AKnight), Biconditional(AKnave, AKnight)),
    Biconditional(Biconditional(AKnave,AKnight),BKnight),
    Biconditional(CKnave, BKnight),
    Biconditional(AKnight,CKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
