import argparse
import json
import os
import random
import shutil
from copy import copy

from typing import List


def main(source_path: str, mbs: List[float], seed: int):
    random.seed(seed)
    assert mbs

    with open(source_path, "rt") as f:
        examples = f.read()
    examples = [example.split("₣") for example in examples.split("␢") if example]

    bs = [mb * 1000000 for mb in mbs]
    folder_name = f"code_golf_{seed}"
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

    filedirs = [[]]

    random.shuffle(examples)
    written_bs = 0
    for filepath, content in examples:
        filepath = filepath.strip()
        filedir = os.path.dirname(filepath)
        os.makedirs(os.path.join(folder_name, filedir), exist_ok=True)
        filedirs[-1].append(filedir)

        with open(os.path.join(folder_name, filepath), "wt") as f:
            written_bs += f.write(content.strip())
        if written_bs > bs[0]:
            written_bs = 0
            bs.pop(0)
            if bs:
                filedirs.append([])
                continue
            else:
                break

    for i, filedir in enumerate(filedirs):
        paths_dict = {"evaluationRoots": filedir}
        with open(os.path.join(folder_name, f"paths_{i}.json"), "wt") as f:
            json.dump(paths_dict, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str)
    parser.add_argument("--sizes", type=float, nargs="+", required=True)
    parser.add_argument("--postfix", type=str, default="")
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    main(args.src, args.sizes, args.seed)
