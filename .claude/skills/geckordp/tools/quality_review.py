"""
Quality review panel for RE case study deliverables.

Dispatches three agents (haiku, sonnet, opus) to independently score D1 (Quality Depth)
against the rubric. Each agent reads the deliverables and scores without seeing the
other agents' scores. The caller then evaluates the three assessments.

This exists because self-assessment is systematically wrong. Session 2 estimated
Grade B (72/100); actual was Grade D (45/100). Every session repeats this error.

Usage (from Claude Code):
    Run three agents in parallel, each with the prompt below customized for the
    model tier. Collect scores. Use median as D1.

    The agents should NOT be told what score to give. They read the rubric,
    read the deliverables, and score independently.
"""

# This is a prompt template, not executable Python.
# The main agent should dispatch three Agent tool calls with this prompt,
# varying only the model parameter.

REVIEW_PROMPT_TEMPLATE = """
You are reviewing reverse engineering deliverables for quality. Score D1 (Quality Depth) only.

## Rubric (D1: Quality Depth, 0-25 points)

| Points | Criteria |
|---|---|
| 0-5 | Surface only: lists scripts, DOM structure, basic features |
| 6-10 | Architecture recovered: module graph, state management pattern, data flow |
| 11-15 | Behavioral edge cases documented, cross-implementation comparison, CSS/visual spec |
| 16-20 | Non-obvious findings: security properties, performance characteristics, framework-imposed vs app-chosen patterns, undocumented API surface |
| 21-25 | Insights the original developers would find valuable: bugs found, design flaws identified, improvement opportunities, patterns transferable to other projects |

## Correctness Gate (must pass for any score above 0)

| Criterion | Pass | Fail |
|---|---|---|
| Factual accuracy | All stated facts verified against source/behavior | Any claim contradicted by evidence |
| Completeness of data model | All fields, types, and constraints documented | Missing fields that affect behavior |
| Behavioral coverage | All user-visible features specified with trigger → behavior | Missing features discoverable by interacting with the app |
| Reproducibility | A competent developer could reimplement from DESIGN.md alone | Spec requires reading the original source to fill gaps |
| No hallucination | Every architectural claim traceable to source or behavioral observation | Architecture described that doesn't exist in the code |

## Your task

1. Read all three deliverables below
2. Check the correctness gate — does it pass?
3. Score D1 (0-25) with specific justification
4. List what's missing that would raise the score
5. List any factual errors or unsupported claims

Be harsh. The purpose of this review is to find problems, not to validate.

## Deliverables

### ARCHITECTURE.md
{architecture_md}

### DESIGN.md
{design_md}

### README.md
{readme_md}

## Output format

```
GATE: Pass / Fail (with reason if fail)
D1_SCORE: <number>/25
JUSTIFICATION: <2-3 sentences>
MISSING: <bullet list>
ERRORS: <bullet list, or "None found">
```
"""


def format_prompt(target_dir):
    """Read deliverables and format the review prompt."""
    import os

    files = {}
    for name in ("ARCHITECTURE.md", "DESIGN.md", "README.md"):
        path = os.path.join(target_dir, name)
        if os.path.exists(path):
            with open(path) as f:
                files[name] = f.read()
        else:
            files[name] = f"[{name} not found]"

    return REVIEW_PROMPT_TEMPLATE.format(
        architecture_md=files["ARCHITECTURE.md"],
        design_md=files["DESIGN.md"],
        readme_md=files["README.md"],
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: quality_review.py <target_dir>")
        print("Prints the review prompt. Dispatch to 3 agents (haiku, sonnet, opus).")
        sys.exit(1)

    print(format_prompt(sys.argv[1]))
