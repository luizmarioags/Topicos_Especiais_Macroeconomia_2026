"""Gera todas as tabelas, matrizes, simulações e figuras de referência."""

from __future__ import annotations

import argparse

from m3e.cli import generate_all


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/python")
    args = parser.parse_args()
    generate_all(args.output_dir)


if __name__ == "__main__":
    main()

