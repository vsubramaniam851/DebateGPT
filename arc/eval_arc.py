import json
import numpy as np
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
    pattern = r"\d+\.?\d*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]

    return None

def parse_answer(input_str):
    pattern = r'(\w)\)'
    matches = re.findall(pattern, input_str)

    solution = None
    for match_str in matches:
        solution = match_str.upper()
        if solution not in ["A", "B", "C", "D"]:
            continue
        if solution:
            break

    return solution

def compute_accuracy(gt, pred_solutions):
    if type(pred_solutions) == list:
        pred_answers = []

        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution)

            if pred_answer is None:
                pred_answer = solve_math_problems(pred_solution)

            if pred_answer is not None:
                pred_answers.append(pred_answer)

        # if pred_answer is None:
        #     return 1
        if pred_answer != None:
            pred_answer = most_frequent(pred_answers)
        # pred_answer = pred_answers[0]
    else:
        pred_answer = parse_answer(pred_solutions)
        if pred_answer is None:
            pred_answer = solve_math_problems(pred_solutions)

    if gt == pred_answer:
        return 1
    else:
        print(question)
        print(pred_solutions, pred_answer, f'{gt}\n')
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

    file = f"{args.save_name}_full-arc.json"
    response_dict = json.load(open(file, "r"))
    questions = list(response_dict.keys())

    accuracies = []
    print(len(questions))

    for question in questions:
        responses, gt = response_dict[question]

        pred_solutions = []
        for response in responses:
            pred_solution = response[-1]["content"]

            pred_solutions.append(pred_solution)
            # break

        # pred_solutions = pred_solutions[:1]

        accurate = compute_accuracy(gt, pred_solutions)


        if accurate is not None:
            accuracies.append(float(accurate))
        else:
            import pdb
            pdb.set_trace()
            print(gt)

    print("accuracies:", np.mean(accuracies), np.std(accuracies) / (len(accuracies) ** 0.5))
    print(file)