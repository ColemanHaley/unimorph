#!/usr/bin/env python3
"""UniMorph: Annotated morphology in the world's languages\n
Quick usage:
    analyze a sentence:
        cat spanish.txt | unimorph -l spa
    download datasets:
        cat iso-codes.txt | xargs -I@ unimorph download --lang @
"""
import argparse
import logging
import sys
from .datawrangle import download_unimorph, get_list_of_datasets
from .language import Language

import pandas as pd

__version__ = "0.1.0"

CITATION = r"""
@inproceedings{Batsuren-et-al-2022,
    title = "{U}ni{M}orph 4.0: Universal Morphology",
    author = {Batsuren, Khuyagbaatar and Goldman, Omer and Khalifa, Salam and 
        Habash, Nizar and Kieraś, Witold and Bella, Gábor and Leonard, Brian and 
        Nicolai, Garrett and Gorman, Kyle and Ate, Yustinus Ghanggo and 
        Ryskina, Maria and Mielke, Sabrina J. and Budianskaya, Elena and 
        El-Khaissi, Charbel and Pimentel, Tiago and Gasser, Michael and 
        Lane, William and Raj, Mohit and Coler, Matt and 
        Samame, Jaime Rafael Montoya and Camaiteri, Delio Siticonatzi and 
        Sagot, Benoît and Rojas, Esaú Zumaeta and Francis, Didier López and 
        Oncevay, Arturo and Bautista, Juan López and 
        Villegas, Gema Celeste Silva and Hennigen, Lucas Torroba and 
        Ek, Adam and Guriel, David and Dirix, Peter and
        Bernardy, Jean-Philippe and Scherbakov, Andrey and
        Bayyr-ool, Aziyana and Anastasopoulos, Antonios and
        Zariquiey, Roberto and Sheifer, Karina and Ganieva, Sofya and
        Cruz, Hilaria and Karahóǧa, Ritván and Markantonatou, Stella and 
        Pavlidis, George and Plugaryov, Matvey and Klyachko, Elena and 
        Salehi, Ali and Angulo, Candy and Baxi, Jatayu and 
        Krizhanovsky, Andrew and Krizhanovskaya, Natalia and 
        Salesky, Elizabeth and Vania, Clara and Ivanova, Sardana and 
        White, Jennifer and Maudslay, Rowan Hall and Valvoda, Josef and 
        Zmigrod, Ran and Czarnowska, Paula and Nikkarinen, Irene and 
        Salchak, Aelita and Bhatt, Brijesh and Straughn, Christopher and 
        Liu, Zoey and Washington, Jonathan North and Pinter, Yuval and 
        Ataman, Duygu and Wolinski, Marcin and Suhardijanto, Totok and 
        Yablonskaya, Anna and Stoehr, Niklas and Dolatian, Hossep and 
        Nuriah, Zahroh and Ratan, Shyam and Tyers, Francis M. and 
        Ponti, Edoardo M. and Aiton, Grant and Arora, Aryaman and 
        Hatcher, Richard J. and Kumar, Ritesh and Young, Jeremiah and 
        Rodionova, Daria and Yemelina, Anastasia and Andrushko, Taras and 
        Marchenko, Igor and Mashkovtseva, Polina and Serova, Alexandra and 
        Prud'hommeaux, Emily and Nepomniashchaya, Maria and 
        Giunchiglia, Fausto and Chodroff, Eleanor and Hulden, Mans and 
        Silfverberg, Miikka and McCarthy, Arya D. and Yarowsky, David and 
        Cotterell, Ryan and Tsarfaty, Reut and Vylomova, Ekaterina},
    booktitle = "Proceedings of the 13th International Conference on Language Resources and Evaluation ({LREC} 2022)",
    month = june,
    year = "2022",
    address = "Marseille, France",
    publisher = "European Language Resources Association (ELRA)",
    url = "https://www.aclweb.org/anthology/2022.lrec-836", }
"""

def parse_args():
    parser = argparse.ArgumentParser(
        __doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "mode", choices={"download", "list", "citation", "inflect", "analyze", "segment", "derive"}
    )
    parser.add_argument("--language", "-l", help="language (3-letter ISO 639-3 code)")
    parser.add_argument("--word", "-w", type=str)
    parser.add_argument("--features", type=str)

    parser.add_argument(
        "--quiet",
        "-q",
        default=False,
        action="store_true",
        help="suppress informative output",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    if args.language is not None and len(args.language) != 3:
        parser.error("--language must be a 3-letter ISO 639-3 code!")

    return args

def main() -> None:
    args = parse_args()

    sys.stdin = open(
        sys.stdin.fileno(), mode="r", encoding="utf-8", buffering=True, newline="\n"
    )
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=True)

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format="unimorph: %(message)s")
        
    if args.mode == "download":
        download_unimorph(args.language)
        sys.exit(0)
    elif args.mode == "list":
        print(list(get_list_of_datasets()))
        sys.exit(0)
    elif args.mode == "citation":
        print(CITATION)
        sys.exit(0)

    # remaining subcommands use language
    lang = Language(args.language)

    if args.mode == "inflect":
        print(
            lang.inflect(args.word, features=args.features), end=""
        )
    elif args.mode == "analyze":
        print(lang.analyze(args.word, all=True).to_csv(sep="\t", index=False, header=None), end="")
    elif args.mode == "segment":
        print(lang.analyze(args.word, segment=True), end="")
    elif args.mode == "derive":
        print(lang.derive(args.word).to_csv(sep="\t", index=False, header=None), end="")
    else:
        raise ValueError(f"Unknown mode {args.mode}")


if __name__ == "__main__":
    main()
