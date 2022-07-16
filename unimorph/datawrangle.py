import os
import logging
import pathlib
import subprocess
import pandas as pd
from typing import List, Sequence
from enum import Enum
from dataclasses import dataclass

USERHOME = pathlib.Path.home()
UNIMORPH_DIR_ = os.environ.get("UNIMORPH", USERHOME / ".unimorph")
UNIMORPH_DIR = pathlib.Path(UNIMORPH_DIR_)

@dataclass(eq=True, frozen=True)
class MorphFile:
    extension: str
    columns: Sequence[str]

class MorphDataType(Enum):
    SEGMENTATIONS = MorphFile(extension=".segmentations", columns=["lemma", "form", "features", "segmentation"])
    DERIVATIONS = MorphFile(extension=".derivations", columns=["lemma", "form", "pos", "morph"])
    INFLECTIONS = MorphFile(extension="", columns=["lemma", "form", "features"])

def is_empty(dir: pathlib.Path) -> bool:
    assert dir.is_dir()
    return list(dir.iterdir()) == []

def not_loaded(lang: str) -> bool:
    output_dir = UNIMORPH_DIR / lang
    return (not output_dir.exists()) or is_empty(output_dir)


def download_unimorph(lang: str):
    output_dir = UNIMORPH_DIR / lang
    output_dir.mkdir(exist_ok=True, parents=True)

    if not_loaded(lang):
        logging.info(f"Downloading unimorph/{lang} to {output_dir}")
        subprocess.run(
            ["git", "clone", f"https://github.com/unimorph/{lang}.git"],
            check=True,
            cwd=UNIMORPH_DIR,
        )
    assert output_dir.is_dir()

def get_list_of_datasets() -> List[str]:
    command = r"""
        for i in {1..2}
        do
          curl -s "https://api.github.com/orgs/unimorph/repos?per_page=100&page=$i"
        done |
          grep ssh_url |
          grep -o 'git@github.com:unimorph/[a-z]\{3\}.git' |
          cut -c25-27
        """

    data = subprocess.run(
        command, shell=True, check=True, capture_output=True, encoding="utf-8"
    )

    return sorted(filter(bool, data.stdout.split("\n")))

def load_dataset(lang: str, datatype: MorphDataType) -> pd.DataFrame: # will return an error if file exists but is not parseable

    download_unimorph(lang)

    language_path = UNIMORPH_DIR / lang / (lang+datatype.value.extension)
    if os.path.exists(language_path):
        data = pd.read_csv(
                language_path, header=None, sep="\t", names=datatype.value.columns
                )
        return data
    tsv = language_path.with_suffix(language_path.suffix + '.tsv')
    if os.path.exists(tsv):
        data = pd.read_csv(
            tsv, header=None, sep="\t", names=datatype.value.columns
        )
        return data
    i = 0
    data = []
    while True:
        # deal with split files (e.g., finnish inflections)
        i += 1
        part_path = f"{language_path}.{i}"
        if not os.path.exists(part_path):
            break
        else:
            data.append(pd.read_csv(
                part_path, header=None, sep="\t", names=datatype.value.columns
            ))
    if len(data) > 0:
        return pd.concat(data)
    else:
        logging.debug(f"Language {lang} lacks file {lang+datatype.value.extension}")
        return None

