import pandas as pd
import json
import time
import random
import openai
import argparse
from tqdm import tqdm

openai_key = None #TODO: Fill this in!
openai.api_key = openai_key

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def generate_answer(answer_context, model = "ft-gpt3.5", temperature = 1):
    if model == "gpt3.5":
        model_str = "gpt-3.5-turbo-0301"
    elif model == "gpt3.5-06":
        model_str = "gpt-3.5-turbo-0613"
    elif model == "ft-gpt3.5":
        model_str = None #TODO: Fill this in!
    else:
        model_str = "gpt-4-0613"
    try:
        completion = openai.ChatCompletion.create(
                  model=model_str,
                  messages=answer_context,
                  temperature = temperature,
                  n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)

    return completion

def parse_question_answer(question):
    sentence = question["sentence"]
    option1 = question["option1"]
    option2 = question["option2"]
    prompt = f"Fill in the blank in the following sentence using one of the two given options?\n\n{sentence}\nOption 1:{option1} Option 2:{option2}\n\nGive your answer as a number, so 1 for option 1 or 2 for option 2 at the end of your response."
    return prompt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action = "store", default = "ft-gpt3.5", type = str, choices = ["gpt3.5", "gpt4", "ft-gpt3.5", "gpt3.5-06"])
    parser.add_argument("--temperature", action = "store", type = float, dest = "temperature", default = 1)
    parser.add_argument("--save_name", action = "store", default = "debategpt", type = str)
    parser.add_argument("--fewshot", action = "store_true", dest = "fewshot")
    parser.add_argument("--data", action = "store", default = "dev", type = str)
    parser.set_defaults(fewshot = False)
    args = parser.parse_args()

    if args.data == "dev":
        with open("winogrande_1.1/dev.jsonl", "r") as f:
            questions = [json.loads(l) for l in f]
        with open("winogrande_1.1/dev-labels.lst", "r") as f:
            answers = f.readlines()
        assert len(questions) == len(answers)
    else:
        with open("winogrande_1.1/test.jsonl", "r") as f:
            questions = [json.loads(l) for l in f]
        answers = [1 for q in questions]

    if args.fewshot:
        with open("winogrande-fewshot.txt", "r") as f:
            few_shot_prompt = f.read()
        system_prompt = {
            "role": "system",
            "content": few_shot_prompt
        }


    random.seed(0)
    response_dict = {}

    for idx in tqdm(range(len(questions)), "Evaluating Winogrande"):
        og_question = questions[idx]
        answer = answers[idx]
        question= parse_question_answer(og_question)
        agent_contexts = [[{"role": "user", "content": question}] for agent in range(1)]
        for i, agent_context in enumerate(agent_contexts):

            completion = generate_answer(agent_context, model = args.model)

            assistant_message = construct_assistant_message(completion)
            agent_context.append(assistant_message)
            print(completion)

        response_dict[question] = (agent_contexts, answer)
    json.dump(response_dict, open("{}_full-winogrande.json".format(args.save_name), "w"))