"""Download the pinned benchmark datasets into bench/data/ and write data/paths.json.

    uv run python fetch_data.py
"""
import hashlib
import json
import urllib.request
from pathlib import Path

from huggingface_hub import hf_hub_download

DATA = Path(__file__).resolve().parent / "data"

HF = {  # key: (repo, file, pinned revision)
    "w2c": ("nvidia/When2Call", "test/when2call_test_mcq.jsonl", "0582f7749d"),
    "clinc": ("clinc/clinc_oos", "plus/test-00000-of-00001.parquet", "155b9c7104"),
    "inj": ("deepset/prompt-injections", "data/test-00000-of-00001-701d16158af87368.parquet", "4f61ecb038"),
    "halu": ("pminervini/HaluEval", "qa/data-00000-of-00001.parquet", "12a856119f"),
}
B77 = "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data"
B77_SHA256 = "d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d"


def main():
    paths = {}
    for key, (repo, fname, rev) in HF.items():
        paths[key] = hf_hub_download(repo, fname, repo_type="dataset", revision=rev,
                                     local_dir=DATA / repo.replace("/", "__"))
    b77 = DATA / "PolyAI__banking77"
    b77.mkdir(parents=True, exist_ok=True)
    for f in ("test.csv", "categories.json"):
        urllib.request.urlretrieve(f"{B77}/{f}", b77 / f)
    got = hashlib.sha256((b77 / "test.csv").read_bytes()).hexdigest()
    if got != B77_SHA256:
        raise SystemExit(f"banking77 test.csv sha256 {got} != pinned {B77_SHA256}")
    paths["b77"] = str(b77 / "test.csv")
    (DATA / "paths.json").write_text(json.dumps(paths, indent=1))
    print(json.dumps(paths, indent=1))


if __name__ == "__main__":
    main()
