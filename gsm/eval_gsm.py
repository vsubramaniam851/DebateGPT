import json
import openai
import numpy as np
import time
import re
import argparse

def parse_bullets(sentence):
    bullets_preprocess = sentence.split("\n")
    bullets = []

    for bullet in bullets_preprocess:
        try:
            idx = bullet.find(next(filter(str.isalpha, bullet)))
        except:
            continue

        bullet = bullet[idx:]

        if len(bullet) != 0:
            bullets.append(bullet)

    return bullets

def parse_yes_no(string):
    """
    Parses a string containing "yes" or "no" and returns a boolean value.

    Args:
        string (str): The string to parse.

    Returns:
        bool: True if the string contains "yes", False if the string contains "no".

    Raises:
        ValueError: If the input string does not contain "yes" or "no".
    """
    if "yes" in string.lower():
        return True
    elif "no" in string.lower():
        return False
    else:
        return None

def solve_math_problems(input_str):
    pattern = r"\d+\.?[\,\d]*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1].replace(",", "")

    return None

def parse_answer(input_str):
    pattern = r"\{([0-9.,$]*)\}"
    new_pattern = r"\{([0-9.,$]*[\{,\}]*[0-9.,$]*)\}"
    matches = re.findall(new_pattern, input_str)

    solution = None

    for match_str in matches[::-1]:
        solution = re.sub(r"[^0-9.]", "", match_str)
        if solution:
            break

    return solution


def compute_accuracy(gt, pred_solution):
    debug = False
    if debug:
        import pdb; pdb.set_trace()
    answers = solve_math_problems(gt)

    if answers is None:
        return None
    if type(pred_solution) == list:
        pred_answers = []
        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution)

            if pred_answer is None or pred_answer == '':
                pred_answer = solve_math_problems(pred_solution)

            pred_answers.append(pred_answer)
        pred_answer = most_frequent(pred_answers)
    else:
        pred_answer = parse_answer(pred_solution)
        if pred_answer is None:
            pred_answer = solve_math_problems(pred_solution)

    if pred_answer is None:
        return 1
    if float(answers) == float(pred_answer):
        return 1
    else:
        print("----------------INCORRECT-----------------------")
        print(question)
        print("------------------------------------")
        print(gt)
        print("------------------------------------")
        print(pred_solutions)
        print("------------------------------------")
        print(answers)
        print("------------------------------------")
        print(pred_answer)
        return 0

def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_name", action = "store", default = "debategpt", type = str)
    args = parser.parse_args()
    response_path = "{}_full-gsm.json"
    response_dict = json.load(open(response_path.format(args.save_name), "r"))

    questions = list(response_dict.keys())

    accuracies = []

    for question in questions:
        responses, gt = response_dict[question]

        pred_solutions = []
        for response in responses:
            pred_solution = response[-1]['content']

            pred_solutions.append(pred_solution)
            # break

        accurate = compute_accuracy(gt, pred_solutions)

        if accurate is not None:
            accuracies.append(float(accurate))
        else:
            import pdb
            pdb.set_trace()
            print(gt)

    print(len(accuracies))
    print("accuracies:", np.mean(accuracies), np.std(accuracies) / (len(accuracies) ** 0.5))