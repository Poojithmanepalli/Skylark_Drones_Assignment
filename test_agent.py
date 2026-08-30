from agent import answer_question


questions = [
    "What is our current pipeline?",
    "What are our top deals?",
    "How are our work orders doing?",
    "Which sectors have the most work orders?",
    "How much is receivable?",
    "What data quality issues do we have?",
    "How is Mining doing?"
]


for question in questions:

    print("\n")
    print("=" * 70)
    print("QUESTION:", question)
    print("=" * 70)

    print(
        answer_question(question)
    )