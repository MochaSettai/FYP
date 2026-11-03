import argparse

from agentless.util.utils import load_jsonl
from agentless.util.model_registry import DEFAULT_MODEL, MODELS, get_price

def cost(fp, model):
    def flatten_trajs(record, trajs):
        if isinstance(record, dict):
            trajs.append(record)
            return
        for r in record:
            flatten_trajs(r, trajs)

    data = load_jsonl(fp)

    sum_prompt, sum_completion = 0, 0
    total = 0

    for record in data:
        for key in record:
            if "traj" not in key:
                continue
            trajs = []
            flatten_trajs(record[key], trajs)
            for r in trajs:
                if "usage" in r:
                    prompt_tokens = r["usage"]["prompt_tokens"]
                    if "completion_tokens" in r["usage"]:
                        completion_tokens = r["usage"]["completion_tokens"]
                    else:
                        completion_tokens = 0
                    sum_prompt += prompt_tokens
                    sum_completion += completion_tokens

        total += 1

    price_in, price_out = get_price(model)
    cost = sum_prompt * price_in / 1000000 + sum_completion * price_out / 1000000
    tokens = sum_prompt + sum_completion

    print(f"Total cost: {cost = }")
    print(f"Avg cost: {cost / total}")

    print(f"Total tokens: {tokens = }")
    print(f"Avg tokens: {tokens / total}")


def embedding_cost(fp):
    data = load_jsonl(fp)

    cost = 0
    total = 0

    for record in data:
        cost += 0.02 * record["traj"]["usage"]["embedding_tokens"] / 1000000
        total += 1

    print(f"Total cost: {cost = }")
    print(f"Avg cost: {total}: {cost / total}")

    return cost


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--embedding_cost", action="store_true")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, choices=list(MODELS))

    args = parser.parse_args()

    if args.embedding_cost:
        embedding_cost(args.output_file)
    else:
        cost(args.output_file, args.model)


if __name__ == "__main__":
    main()
