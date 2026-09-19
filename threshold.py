#!/usr/bin/env python3
"""
threshold - work out who an automated decision system gets wrong.

No dependencies. Python 3.8+.

    python3 threshold.py                  # walk the built-in examples
    python3 threshold.py --preset fraud
    python3 threshold.py --accuracy 0.99 --false-alarm 0.01 --rate 0.001 --pop 100000
"""

import argparse
import math
import sys

BLUE = "\033[38;5;75m"
GREY = "\033[38;5;243m"
WHITE = "\033[97m"
OFF = "\033[0m"


def phi(z):
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def outcomes(detection_rate, false_alarm_rate, base_rate, population):
    """The four cells every automated decision produces."""
    real = population * base_rate
    clean = population - real
    tp = real * detection_rate
    fn = real - tp
    fp = clean * false_alarm_rate
    tn = clean - fp
    flagged = tp + fp
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "flagged": flagged,
        "precision": tp / flagged if flagged else 0.0,
        "recall": detection_rate,
    }


def bar(share, width=46):
    filled = max(0, min(width, round(share * width)))
    return "#" * filled + "-" * (width - filled)


def report(name, detection_rate, false_alarm_rate, base_rate, population, color=True):
    r = outcomes(detection_rate, false_alarm_rate, base_rate, population)
    b, w, g, o = (BLUE, WHITE, GREY, OFF) if color else ("", "", "", "")
    wrong = 1 - r["precision"]

    print(f"\n{g}>{o} {w}{name}{o}")
    print(f"{g}  detection rate {detection_rate:>8.1%}   "
          f"false alarms {false_alarm_rate:>7.2%}   "
          f"base rate {base_rate:>7.3%}{o}")
    print(f"{g}  population {population:>12,.0f}{o}\n")

    print(f"   flagged by model   {bar(1.0)}  {r['flagged']:>10,.0f}")
    share = r["precision"]
    print(f"   {b}actually real      {bar(share)}  {r['true_positive']:>10,.0f}{o}")
    print(f"   missed entirely    {' ' * 46}  {r['false_negative']:>10,.0f}")
    print()
    print(f"   {b}{wrong:.0%} of every flag is a person who did nothing.{o}")
    print(f"{g}   precision {r['precision']:.2%}   recall {r['recall']:.2%}{o}")


PRESETS = {
    "fraud": ("card fraud detection", 0.99, 0.01, 0.001, 100_000),
    "hiring": ("resume screening", 0.58, 0.16, 0.08, 3_000),
    "screening": ("disease screening", 0.96, 0.036, 0.005, 100_000),
    "moderation": ("content moderation", 0.76, 0.067, 0.01, 1_000_000),
}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Work out who an automated decision system gets wrong.")
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--accuracy", type=float,
                    help="share of real cases the model catches, 0-1")
    ap.add_argument("--false-alarm", type=float,
                    help="share of clean cases the model flags anyway, 0-1")
    ap.add_argument("--rate", type=float,
                    help="how common the thing actually is, 0-1")
    ap.add_argument("--pop", type=float, default=100_000,
                    help="how many cases go through (default 100000)")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args(argv)

    color = not args.no_color and sys.stdout.isatty()

    if args.accuracy is not None:
        missing = [n for n, v in (("--false-alarm", args.false_alarm),
                                  ("--rate", args.rate)) if v is None]
        if missing:
            ap.error("also needs " + " and ".join(missing))
        report("custom", args.accuracy, args.false_alarm, args.rate,
               args.pop, color)
    elif args.preset:
        name, d, f, r, p = PRESETS[args.preset]
        report(name, d, f, r, p, color)
    else:
        for key in sorted(PRESETS):
            name, d, f, r, p = PRESETS[key]
            report(name, d, f, r, p, color)

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
