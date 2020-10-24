import re
import sys
from classifier import Classifier

'''
Authors:
Daan Krol (s3142221)
Niels Rocholl (s3501108)
Niels Rocholl (s3501108)
Julian Bruinsma (s3215601)
'''

def main():
    classifier = Classifier()
    print_example_questions()
    for question in sys.stdin:
        module = classifier.classify(question)
        if module is None:
            print("Could not classify the question")
        else:
            answer = module.answer()
            if answer:
                print("Answer:")
                # Remove duplicates from list
                answer = list(set(answer))
                # Remove urls from answers
                answer = [a for a in answer if not a.startswith('http://')]
                for a in answer:
                    is_date = re.search("(.*)(T00:00:00Z)", a)
                    if is_date:
                        print(is_date.group(1))
                    else:
                        print(a)
            else:
                print("Could not answer the question.")

    exit()


def print_example_questions():
    print("Printing example questions:")
    example_questions = [
        'What is the density of ice?',
        'What is the chemical formula for dopamine?',
        'What is the cause of Anthrax?',
        'What is the boiling point of water?',
        'What is the atomic number of silver?',
        'What is the field of work of CERN?',
        'What is the half-life of uranium-235?',
        'Who is the inventor of the automobile?',
        'Who is the mother of Isaac Newton?',
        'Who are the founders of Nvidia?'
    ]
    test_questions = [
        "At what speed does a photon move?",
        "How big is the Milky Way?",
        "How many awards has Albert Einstein received?",
        "How many languages did Nikola Tesla speak?",
        "Name all crew members of the Apollo 15 mission.",
        "Penicilin was discovered by whom?",
        "What are the effects of a tsunami?",
        "Is HTML a markup language?",
        "When was the Doppler effect discovered?",
        "Where did Carl Linnaeus study?"
    ]

    for tq in test_questions:
        print(tq)


if __name__ == "__main__":
    main()
