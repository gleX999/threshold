# threshold

Work out who an automated decision system gets wrong.

You give it three numbers a company would quote you — how often the model
catches real cases, how often it flags clean ones anyway, and how common the
thing actually is. It gives you the number nobody quotes: **of everyone this
system accuses, how many did nothing.**

Live version, no install: **[threshold on the web](https://claude.ai/artifact/8wMiAUghvLmpakMEtzBfzq)**

```
$ python3 threshold.py --preset fraud

> card fraud detection
  detection rate    99.0%   false alarms   1.00%   base rate  0.100%
  population      100,000

   flagged by model   ##############################################       1,098
   actually real      ####------------------------------------------          99
   missed entirely                                                             1

   91% of every flag is a person who did nothing.
   precision 9.02%   recall 99.00%
```

A fraud model that is 99% accurate accuses 1,098 people. Ninety-nine of them
did something. The model is not broken and nobody lied about the accuracy.

## Why the accuracy number misleads

Accuracy is measured on the model. Being right about *you* depends on the model
**and** on how rare the thing is that it hunts. Those are different numbers and
only the second one affects your life.

Out of 100,000 transactions where 0.1% are fraud:

| | real fraud | clean |
|---|---|---|
| **flagged** | 99 | 999 |
| **passed** | 1 | 98,901 |

The model catches almost every real case. It also flags 1% of a very large
clean group, and 1% of 99,900 is bigger than all the fraud that exists. Hunt
something rare with an imperfect net and most of what you catch is the wrong
thing.

## Install

None. Python 3.8 or newer, standard library only.

```bash
git clone https://github.com/gleX999/threshold
```

## Use

```bash
python3 threshold.py                     # all built-in examples
python3 threshold.py --preset hiring     # fraud | hiring | screening | moderation
python3 threshold.py --accuracy 0.95 --false-alarm 0.02 --rate 0.004 --pop 250000
```

| flag | meaning |
|---|---|
| `--accuracy` | share of real cases the model catches (recall), 0–1 |
| `--false-alarm` | share of clean cases it flags anyway, 0–1 |
| `--rate` | how common the thing actually is, 0–1 |
| `--pop` | how many cases go through |

Import it instead, if that is more useful:

```python
from threshold import outcomes

r = outcomes(detection_rate=0.99, false_alarm_rate=0.01,
             base_rate=0.001, population=100_000)

r["precision"]       # 0.0902
r["false_positive"]  # 999.0
```

## The math

Four counts, from three inputs and a population `N`:

```
real  = N × base_rate
clean = N − real

true positives   = real  × detection_rate
false negatives  = real  − true positives
false positives  = clean × false_alarm_rate
true negatives   = clean − false positives

precision = TP / (TP + FP)     of everyone flagged, how many deserved it
recall    = TP / (TP + FN)     of everyone who deserved it, how many were caught
```

Precision is Bayes' theorem written out: the probability that a flag is real
depends on the base rate, not only on how good the model is.

The web version adds the part the command line leaves out. It puts the two
groups on a shared score and lets you drag the line that separates them.
Raising the line means fewer innocent people flagged and more real cases
missed; lowering it means the reverse. You cannot improve both. You can only
choose which error to make, and therefore who absorbs it — and the errors that
cost the institution money are the ones that get fixed.

Nothing in training produces that line. A person picks it.

## Limits, stated plainly

The web version models the two groups as normal distributions with equal
spread. Real score distributions are messier and often skewed. The shape
changes the exact trade-off between the two errors; it does not change the
conclusion, which is driven by the base rate.

The command line version assumes nothing about shape at all — it takes the two
rates you supply and does arithmetic.

## Longer write-up

[The Five Equations That Quietly Run Every Algorithm That Judges You](https://x.com/glex999/status/2101312586553733450?s=46)

## License

MIT
