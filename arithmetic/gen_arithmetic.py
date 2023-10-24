import openai
import json
import numpy as np
import time
import pickle
from tqdm import tqdm
import argparse

openai.api_key = None #TODO: Fix this!

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

def generate_answer(answer_context, model = "gpt3.5"):
    if model == "gpt3.5":
        model_str = "gpt-3.5-turbo-0613"
    elif model == "ft-gpt3.5":
        model_str = None #TODO: Fix this!
    else:
        model_str = "gpt-4-0613"
    try:
        completion = openai.ChatCompletion.create(
                  model = model_str,
                  messages=answer_context,
                  n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)

    return completion

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def parse_answer(sentence):
    parts = sentence.split(" ")

    for part in parts[::-1]:
        try:
            answer = float(part)
            return answer
        except:
            continue

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
    answer = parse_answer("My answer is the same as the other agents and AI language model: the result of 12+28*19+6 is 550.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action = "store", default = "gpt3.5", type = str, choices = ["gpt3.5", "gpt4", "ft-gpt3.5", "gpt3.5-06"])
    parser.add_argument("--save_name", action = "store", default = "debategpt", type = str)
    args = parser.parse_args()
    np.random.seed(0)

    evaluation_round = 1000
    scores = []

    generated_description = {}

    for round in tqdm(range(evaluation_round)):
        a, b, c, d, e, f = np.random.randint(0, 30, size=6)

        answer = a + b * c + d - e * f
        agent_contexts = [[{"role": "user", "content": """What is the result of {}+{}*{}+{}-{}*{}? Make sure to state your answer at the end of the response.""".format(a, b, c, d, e, f)}] for agent in range(agents)]

        content = agent_contexts[0][0]['content']
        question_prompt = "We seek to find the result of {}+{}*{}+{}-{}*{}?".format(a, b, c, d, e, f)

        for i, agent_context in enumerate(agent_contexts):
            completion = generate_answer(agent_context, model = args.model)

            assistant_message = construct_assistant_message(completion)
            agent_context.append(assistant_message)
            print(completion)

        text_answers = []

        for agent_context in agent_contexts:
            text_answer = string =  agent_context[-1]['content']
            text_answer = text_answer.replace(",", ".")
            text_answer = parse_answer(text_answer)

            if text_answer is None:
                continue

            text_answers.append(text_answer)

        generated_description[(a, b, c, d, e, f)] = (agent_contexts, answer)

        try:
            text_answer = most_frequent(text_answers)
            if text_answer == answer:
                scores.append(1)
            else:
                scores.append(0)
        except:
            continue

        print("performance:", np.mean(scores), np.std(scores) / (len(scores) ** 0.5))

    pickle.dump(generated_description, open("{}_full-arithmetic.p".format(args.save_name), "wb"))
    import pdb
    pdb.set_trace()
    print(answer)
    print(agent_context)