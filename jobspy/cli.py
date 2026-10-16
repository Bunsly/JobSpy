from __future__ import annotations

import argparse
import io
import json
import logging
import os
import signal
import sys
import textwrap
from collections.abc import Sequence
from functools import partial
from importlib.metadata import version

import pandas as pd

from jobspy import scrape_jobs
from jobspy.model import JobPost, JobType, ScraperInput

FIELDS = list(JobPost.model_fields)
PREVIEW = (
    "site title company location date_posted job_type is_remote min_amount max_amount"
    " currency interval job_url"
).split()
SITES = [site.value for site in ScraperInput.model_validate({}).site_name]
DEFAULT_SITES = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
REGIONS = {
    "bayt": "Middle East",
    "naukri": "India",
    "bdjobs": "Bangladesh",
    "hellowork": "France",
}

DESCRIPTION = """\
Search job boards and print one JSON object per job (JSON Lines) on stdout.
Default: 5 jobs from each of 4 boards; --site picks boards, -n sets the count.
Errors and warnings go to stderr.

examples:
  jobspy "software engineer" --site indeed,linkedin --location Chicago -n 20
  jobspy nurse --site indeed,linkedin --hours-old 24 -o jobs.jsonl
  jobspy "data analyst" --remote --fields title,company,job_url

exit codes:
  0    at least one board answered, also with no jobs
  1    every board failed
  2    usage error
  130  interrupted
"""


def listing(title: str, names: Sequence[str]) -> str:
    text = textwrap.fill(
        ", ".join(names), 78, initial_indent="  ", subsequent_indent="  "
    )
    return f"{title}:\n{text}\n"


EPILOG = "\n".join(
    [
        "boards:\n  "
        + ", ".join(DEFAULT_SITES)
        + " (default)\n  "
        + ", ".join(f"{s} ({REGIONS[s]})" for s in SITES if s in REGIONS)
        + "\n",
        listing("job types", [t.value for t in JobType]),
        listing("default fields", PREVIEW),
        listing(
            "other fields (--fields takes any of these, or all)",
            [f for f in FIELDS if f not in PREVIEW],
        ),
    ]
)


def commas(text: str) -> list[str]:
    return [part.strip() for part in text.split(",")]


def fields(text: str) -> list[str]:
    names = FIELDS if text == "all" else commas(text)
    if unknown := [name for name in names if name not in FIELDS]:
        raise argparse.ArgumentTypeError(
            f"unknown {', '.join(unknown)}; use all or any of {', '.join(FIELDS)}"
        )
    return list(dict.fromkeys(names))


def parser() -> argparse.ArgumentParser:
    formatter = partial(argparse.RawDescriptionHelpFormatter, max_help_position=30)
    p = argparse.ArgumentParser(
        prog="jobspy",
        usage="%(prog)s [QUERY] [options]",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=formatter,
        argument_default=argparse.SUPPRESS,
        allow_abbrev=False,
    )
    if sys.version_info >= (3, 14):
        p.color = False
    p.add_argument(
        "-V", "--version", action="version", version=version("python-jobspy")
    )
    add = p.add_argument_group("search").add_argument
    add("search_term", nargs="?", metavar="QUERY", help="search term")
    add("--location", metavar="TEXT", help="city, state or country")
    add("--distance", metavar="N", help="miles (default 50)")
    add("--remote", dest="is_remote", action="store_true", help="remote jobs only")
    add("--job-type", metavar="T", help="one of the job types below")
    add("--hours-old", metavar="N", help="posted in the last N hours")
    add("--easy-apply", action="store_true", help="jobs hosted on the board")
    add("--country-indeed", metavar="C", help="Indeed and Glassdoor (default usa)")
    add("-n", "--results-wanted", metavar="N", default=5, help="per board (default 5)")
    add("--offset", metavar="N", help="skip the first N results")
    add = p.add_argument_group("boards").add_argument
    add(
        "--site",
        dest="site_name",
        type=commas,
        default=DEFAULT_SITES,
        metavar="LIST",
        help="comma list (default: see boards below)",
    )
    add(
        "--fetch-description",
        action="store_true",
        help="fetch each job's page (one request per job)",
    )
    add("--description-format", metavar="F", help="markdown (default), html, plain")
    add("--enforce-annual-salary", action="store_true", help="convert pay to yearly")
    add(
        "--linkedin-company-ids",
        type=commas,
        metavar="IDS",
        help="LinkedIn company ids",
    )
    add("--proxies", type=commas, metavar="LIST", help="comma list; or set HTTPS_PROXY")
    add("--ca-cert", metavar="PATH", help="CA bundle for the proxy")
    add("--user-agent", metavar="TEXT", help="User-Agent header")
    add = p.add_argument_group("output").add_argument
    add("--fields", type=fields, metavar="LIST", help="see below")
    add(
        "-o",
        "--output",
        metavar="FILE",
        help="also save full records (.csv, .json or .jsonl)",
    )
    level = p.add_argument_group("diagnostics", "stderr shows warnings by default")
    add = level.add_mutually_exclusive_group().add_argument
    add("-q", "--quiet", action="store_const", dest="verbose", const=0, help="errors")
    add("-v", "--verbose", action="store_const", dest="verbose", const=2, help="info")
    return p


def records(jobs: pd.DataFrame, names: list[str]) -> list[dict[str, object]]:
    return [
        {name: rec[name] for name in names if not pd.isna(rec[name])}
        for rec in jobs[names].to_dict("records")
    ]


def dumps(value: object) -> str:
    return json.dumps(value, default=str, ensure_ascii=False, separators=(",", ":"))


def lines(jobs: pd.DataFrame, names: list[str]) -> list[str]:
    return [dumps(rec) + "\n" for rec in records(jobs, names)]


def main(argv: Sequence[str] | None = None) -> int:
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    p = parser()
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        p.print_help()
        return 0
    args = vars(p.parse_args(argv))
    names, output = args.pop("fields", PREVIEW), args.pop("output", None)
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")
    try:
        jobs = scrape_jobs(**args)
    except ValueError as error:
        p.error(str(error))
    if output:
        try:
            if output.lower().endswith(".csv"):
                jobs.to_csv(output, index=False)
            else:
                with open(output, "w", encoding="utf-8") as saved:
                    if output.lower().endswith(".json"):
                        saved.write(dumps(records(jobs, FIELDS)))
                    else:
                        saved.writelines(lines(jobs, FIELDS))
        except OSError as error:
            p.error(f"cannot write {output}: {error.strerror or error}")
        print(f"saved {len(jobs)} jobs to {output}", file=sys.stderr)
    try:
        sys.stdout.writelines(lines(jobs, names))
        sys.stdout.flush()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1
    failed = set(args["site_name"]) <= jobs.attrs["errors"].keys()
    return int(jobs.empty and failed)
