# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Exa POST /answer: cited LLM answer. `stream` (SSE) is not exposed; output is JSON only.

Docs: https://exa.ai/docs/exa-spec.yaml (AnswerRequest), https://exa.ai/docs/reference/answer
Usage: uv run exa_answer.py "<query>" [--model exa|exa-pro|exa-research|exa-fast] [--system-prompt TEXT] [--text] [--output-schema JSON|@file]
"""
import argparse

import _post_common as pc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("query")
    ap.add_argument("--model", choices=["exa", "exa-pro", "exa-research", "exa-fast"])
    ap.add_argument("--system-prompt")
    ap.add_argument("--text", action="store_true", help="include full page text in citations")
    ap.add_argument("--output-schema", help="JSON Schema draft 7 object, or @file")
    args = ap.parse_args(argv)
    body = {"query": args.query}
    if args.model:
        body["model"] = args.model
    if args.system_prompt:
        body["systemPrompt"] = args.system_prompt
    if args.text:
        body["text"] = True
    if args.output_schema:
        body["outputSchema"] = pc.load_json_arg(args.output_schema)
    pc.run("exa", "POST", "/answer", body)


if __name__ == "__main__":
    main()
