import os, sys
import numpy as np
import pandas as pd
import time
import openai
import json
import argparse
from tqdm import tqdm

openai.api_key = None #TODO: Fill in here!

def generate_answer(answer_context):
    model_name = "gpt-3.5-turbo-0301"
    try:
        completion = openai.ChatCompletion.create(
                  model=model_name,
                  messages=answer_context,
                  n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)

    return completion

def summarize_message(agent_contexts, question_prompt, agent_indices, current_agent):
    prefix_string = f"Here are a list of opinions different agents with the confidence in their opinion to the question, {question_prompt}: "

    for i, agent in enumerate(agent_contexts):
        agent_idx = agent_indices[i]
        if agent_idx < current_agent:
            agent_response = agent[-3]["content"]
        else:
            agent_response = agent[-1]["content"]
        response = "\n\n One agent response: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    prefix_string = prefix_string + "\n\n Please summarize the responses from different agents by consolidating the responses from the agents into one response for the given question"
    agent_context = [{"role": "user", "content": prefix_string}]
    completion = generate_answer(agent_context)
    print(completion)
    content = completion["choices"][0]["message"]["content"]

    return content, completion

def construct_sum_debate(content, question):
    prefix_string = f"These are the recent/updated opinions with confidence scores out of 100 from other agents: \n\n{content}"
    prefix_string = prefix_string + "\n\n Using these opinions carefully as additional advice, can you provide an updated answer to the question {}\n\nExplain your answer.".format(question)
    return {"role": "user", "content": prefix_string}

def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def generation(alpaca_df, agents, rounds):
    generated_description = {}
    for prompt in tqdm(alpaca_df["prompt"]):
        agent_contexts = [[{"role": "user", "content": prompt + "\n\nExplain your answer. Additionally rank your confidence in your response on a scale from 1-100, 1 being least confident and 100 being most confident."}] for agent in range(agents)]
        question_prompt = prompt
        try:
            for round in range(rounds):
                for i, agent_context in enumerate(agent_contexts):
                    if round != 0:
                        agent_contexts_other = agent_contexts[:i] + agent_contexts[i+1:]
                        other_agent_indices = list(range(0, i)) + list(range(i+1, agents))
                        sum_content, message = summarize_message(agent_contexts_other, question_prompt, other_agent_indices, i)
                        message = construct_sum_debate(sum_content, question_prompt)
                        agent_context.append(message)
                        print("message: ", message)

                    completion = generate_answer(agent_context)

                    assistant_message = construct_assistant_message(completion)
                    agent_context.append(assistant_message)
                    print(completion)
            generated_description[prompt] = agent_contexts
        except KeyboardInterrupt:
            return generated_description
        except:
            return generated_description
    return generated_description

def clean_response(question, agent_response):
    question = question["content"]
    agent_response = agent_response["content"]
    user_message = f"""
    Here is a response from an agent to the following question.

    Question: '{question}'
    Agent Response: '{agent_response}'

    Can you condense the response so it only contains relevant information while still answering the question? Give your answer as "Response: "
    """
    prompt = {
        "role": "user",
        "content": user_message
    }
    messages = [prompt]
    completion = generate_answer(messages)
    # print(completion)
    sum_response = completion["choices"][0]["message"]["content"]
    sum_response = sum_response.replace("Response: ", "")
    return {
        "role": "assistant",
        "content": sum_response
    }

def create_jsonl(args, description, filename):
    dataset_ex = []
    for prompt in tqdm(description):
        agent_contexts = description[prompt]
        agent_responses = []
        question = agent_contexts[0][0]
        for agent in agent_contexts:
            final_agent_response = agent[-1]
            agent_responses.append(final_agent_response)
        #Randomly sample the response from one of the agents
        agent_response = np.random.choice(agent_responses)
        if args.clean:
            agent_response = clean_response(question, agent_response)
        dataset_ex.append({"messages": [question, agent_response]})
    with open(f"{args.save_path}/{filename}.jsonl", "w") as f:
        for entry in dataset_ex:
            json.dump(entry, f)
            f.write("\n")
    return dataset_ex

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", action = "store", type = int, dest = "agents", default = 4)
    parser.add_argument("--rounds", action = "store", type = int, dest = "rounds", default = 3)
    parser.add_argument("--data_path", action = "store", type = str, dest = "data_path", default = os.path.join("data"))
    parser.add_argument("--save_path", action = "store", type = str, dest = "save_path", default = "ft_data")
    parser.add_argument("--batch_size", action = "store", type = str, dest = "batch_size", default = 500)
    parser.add_argument("--structure", type = str, action = "store", default = "final", dest = "structure", choices = ["per", "combined", "final"])
    parser.add_argument("--filename", type = str, default = None, action = "store", dest = "filename")
    parser.add_argument("--clean", action = "store_true", dest = "clean")
    parser.set_defaults(clean = False)
    args = parser.parse_args()
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)
    train_df = pd.read_csv(f"{args.data_path}/5k_alpaca_ft.csv")
    train_description = generation(train_df, args.agents, args.rounds)
    if not args.filename:
        args.filename = "alpaca-ft-train"
    train_dataset = create_jsonl(args, train_description, args.filename, args.structure)
    pass