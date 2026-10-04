import argparse, asyncio, json
from pathlib import Path
from .domain import AnalyzeRequest
from .engine import AgentShieldEngine

def main():
    p = argparse.ArgumentParser(prog="agentshield")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("file")
    args = p.parse_args()
    if args.cmd == "analyze":
        req = AnalyzeRequest.model_validate_json(Path(args.file).read_text())
        out = asyncio.run(AgentShieldEngine().analyze(req))
        print(out.model_dump_json(indent=2))
