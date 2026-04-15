# AGENTS.md

## What this repo is
- This repo is a single-script installer/migrator for SkillPointer; `setup.py` is the source of truth for behavior.
- There is no test/lint/typecheck pipeline in-repo; verify changes by running `python setup.py` against a safe skills sandbox.

## Real entrypoints
- OpenCode mode (default): `python setup.py`
- Claude mode: `python setup.py --agent claude`
- Windows wrappers call compatibility mode: `python setup.py install` (`Install.bat`, `Install.vbs`)

## Safety-critical behavior (easy to miss)
- `setup.py` is stateful and mutates user directories under `$HOME`; it is not a dry-run tool.
- If a destination skill folder already exists in the hidden vault, it is deleted via `shutil.rmtree(dest)` before move.
- Migration skips only:
  - folders ending with `-category-pointer`
  - empty folders
- Script exits early if active skills directory does not exist.

## Paths and mode switching
- OpenCode paths:
  - active skills: `~/.config/opencode/skills`
  - hidden vault: `~/.opencode-skill-libraries`
- Claude paths:
  - active skills: `~/.claude/skills`
  - hidden vault: `~/.skillpointer-vault`

## Categorization and pointer generation
- Category assignment is heuristic and name-based (`DOMAIN_HEURISTICS` in `setup.py`), with `_uncategorized` fallback.
- Pointer generation scans the hidden vault recursively for `SKILL.md` and creates one `*-category-pointer/SKILL.md` per non-empty category.
- Pointer text is generated from the in-script template; keep pointer instructions in sync by editing `pointer_template` in `setup.py`, not by hand-editing generated pointers.

## Editing guidance for future agents
- Prefer minimal edits in `setup.py`; this script is the product.
- If changing category logic, update only `DOMAIN_HEURISTICS` and/or `get_category_for_skill`.
- If changing user-facing pointer instructions, update `pointer_template` and regenerate pointers; do not patch generated output as source of truth.


## What Are Skills?
Source: https://agentskills.io/what-are-skills

> Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.

At its core, a skill is a folder containing a `SKILL.md` file. This file includes metadata (`name` and `description`, at minimum) and instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, templates, and reference materials.

```directory theme={null}
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

### How skills work

Skills use **progressive disclosure** to manage context efficiently:

1. **Discovery**: At startup, agents load only the name and description of each available skill, just enough to know when it might be relevant.

2. **Activation**: When a task matches a skill's description, the agent reads the full `SKILL.md` instructions into context.

3. **Execution**: The agent follows the instructions, optionally loading referenced files or executing bundled code as needed.

This approach keeps agents fast while giving them access to more context on demand.

### The SKILL.md file

Every skill starts with a `SKILL.md` file containing YAML frontmatter and Markdown instructions:

```mdx theme={null}
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
---

# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

## How to extract text
1. Use pdfplumber for text extraction...

## How to fill forms
...
```

The following frontmatter is required at the top of `SKILL.md`:

* `name`: A short identifier
* `description`: When to use this skill

The Markdown body contains the actual instructions and has no specific restrictions on structure or content.

This simple format has some key advantages:

* **Self-documenting**: A skill author or user can read a `SKILL.md` and understand what it does, making skills easy to audit and improve.

* **Extensible**: Skills can range in complexity from just text instructions to executable code, assets, and templates.

* **Portable**: Skills are just files, so they're easy to edit, version, and share.