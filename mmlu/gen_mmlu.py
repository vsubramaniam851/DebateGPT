from glob import glob
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

def generate_answer(answer_context, model = "gpt3.5", temperature = 1):
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

def parse_question_answer(df, ix):
    question = df.iloc[ix, 0]
    a = df.iloc[ix, 1]
    b = df.iloc[ix, 2]
    c = df.iloc[ix, 3]
    d = df.iloc[ix, 4]

    prompt = "Can you answer the following question as accurately as possible? {}: A) {}, B) {}, C) {}, D) {}\n\nExplain your answer. You must pick one of the choices. You are required to put only the final answer choice in the form \"(X)\" at the END of your response.".format(question, a, b, c, d)
    answer = df.iloc[ix, 5]

    return prompt, answer, question

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action = "store", default = "ft-gpt3.5", type = str, choices = ["gpt3.5", "gpt4", "ft-gpt3.5", "gpt3.5-06"])
    parser.add_argument("--temperature", action = "store", type = float, dest = "temperature", default = 1)
    parser.add_argument("--save_name", action = "store", default = "debategpt", type = str)
    parser.add_argument("--fewshot", action = "store_true", dest = "fewshot")

    parser.set_defaults(fewshot = False)
    args = parser.parse_args()
    print("MMLU full evaluation")

    tasks = glob("data/test/*.csv")
    dfs = [pd.read_csv(df) for df in tasks]
    random.seed(0)
    response_dict = {}

    if args.fewshot:
        with open("mmlu-fewshot.txt", "r") as f:
            few_shot_prompt = f.read()
        system_prompt = {
            "role": "system",
            "content": few_shot_prompt
        }

    for df in tqdm(dfs, desc = "Evaluating MMLU"):
        for idx in range(len(df)):
            question, answer, og_question = parse_question_answer(df, idx)
            if args.fewshot:
                agent_contexts = [[system_prompt, {"role": "user", "content": question}] for agent in range(1)]
            else:
                agent_contexts = [[{"role": "user", "content": question}] for agent in range(1)]
            for i, agent_context in enumerate(agent_contexts):
                completion = generate_answer(agent_context, model = args.model, temperature = args.temperature)
                assistant_message = construct_assistant_message(completion)
                agent_context.append(assistant_message)
                print(completion)

            response_dict[question] = (agent_contexts, answer)
    json.dump(response_dict, open("{}_full-mmlu.json".format(args.save_name), "w"))