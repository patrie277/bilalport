def normaliser_reponse(reponse):
    return reponse.strip().lower().replace("(", "").replace(")", "")


def poser_question(question, r1, r2, r3, r4, choix_bonne_reponse):
    print(question)
    print(r1)
    print(r2)
    print(r3)
    print(r4)
    print()

    reponse = input("Votre réponse : ").strip()
    if normaliser_reponse(reponse) == normaliser_reponse(choix_bonne_reponse):
        print("Bonne réponse")
    else:
        print("Mauvaise réponse")


poser_question(
    "Quelle est la capitale de la France ?",
    "(a) Paris",
    "(b) Nice",
    "(c) Lyon",
    "(d) Nantes",
    "(a)",
)

poser_question(
    "Quelle est la capitale de l'Italie ?",
    "(a) Rome",
    "(b) Venise",
    "(c) Pise",
    "(d) Florence",
    "(a)",
)
