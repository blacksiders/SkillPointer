import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

# ==========================================
# 🎯 SkillPointer
# Infinite Context. Zero Token Tax.
# ==========================================


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


# Global configuration state
CONFIG = {
    "agent_name": "OpenCode",
    "active_skills_dir": Path.home() / ".config" / "opencode" / "skills",
    "hidden_library_dir": Path.home() / ".opencode-skill-libraries",
    # Additional directories to scan for skills (e.g. ~/.agents/skills/)
    "extra_skills_dirs": [
        Path.home() / ".agents" / "skills",
    ],
}

# ==========================================
# Categorization Engine
# ==========================================
#
# How matching works:
#   1. PREFIX_OVERRIDES are checked first (highest priority). If the skill
#      name starts with a known prefix, it's immediately assigned.
#   2. DOMAIN_HEURISTICS are checked next. Each keyword is matched against
#      word-boundary-separated tokens of the skill name using regex
#      (\b or start/end of string), NOT naive substring containment.
#      Keywords ending with "-" are treated as prefix matches.
#   3. If nothing matches, the skill goes to "_uncategorized".
#
# To add a new skill that doesn't categorize correctly:
#   - Preferred: add a PREFIX_OVERRIDES entry (most specific, zero side effects)
#   - Alternative: add a keyword to the relevant category in DOMAIN_HEURISTICS
#     (but verify it won't collide with other skill names)

# Prefix overrides: checked FIRST, highest priority.
# Key = prefix the skill name must start with, Value = category.
PREFIX_OVERRIDES = {
    "gsap": "animation",
    "threejs": "3d-graphics",
    "three-js": "3d-graphics",
    "n8n": "automation",
    "fossflow": "architecture",
    "isoflow": "architecture",
    "pretty-mermaid": "tooling",
    "mermaid": "tooling",
    "shadcn": "web-dev",
    "nuqs": "web-dev",
    "claude": "ai-ml",
    "mui": "web-dev",
    "openapi": "backend-dev",
}

# Advanced Heuristic Engine for Universal Categorization
# Keywords are matched at word boundaries, not as raw substrings.
DOMAIN_HEURISTICS = {
    "security": [
        "attack",
        "injection",
        "vulnerability",
        "xss",
        "penetration",
        "privilege",
        "fuzzing",
        "auth",
        "jwt",
        "oauth",
        "bypass",
        "malware",
        "forensics",
        "hacker",
        "wireshark",
        "nmap",
        "security",
        "exploit",
        "encryption",
    ],
    "code-review": [
        "code-review",
        "codereview",
        "pr-review",
        "review-agent",
        "reviewer",
        "review-bot",
        "static-analysis",
        "quality-gate",
        "sonarqube",
    ],
    "git": [
        "git",
        "github",
        "gitlab",
        "pull-request",
        "merge-request",
        "commit",
        "branch",
        "rebase",
        "cherry-pick",
        "stash",
        "conventional-commits",
    ],
    "ai-ml": [
        "ai",
        "ml",
        "llm",
        "gpt",
        "claude",
        "gemini",
        "openai",
        "anthropic",
        "rag",
        "diffusion",
        "huggingface",
        "pytorch",
        "tensorflow",
        "comfy",
        "flux",
        "machine-learning",
        "deep-learning",
        "vision",
        "nlp",
        "seedance",
    ],
    "web-dev": [
        "angular",
        "react",
        "vue",
        "tailwind",
        "frontend",
        "css",
        "html",
        "nextjs",
        "svelte",
        "astro",
        "web",
        "dom",
        "ui-patterns",
        "vercel",
        "shopify",
        "styles",
        "sass",
        "less",
        "bootstrap",
        "shadcn",
        "domain-name",
    ],
    "backend-dev": [
        "api",
        "nestjs",
        "express",
        "django",
        "flask",
        "fastapi",
        "spring",
        "laravel",
        "node",
        "graphql",
        "rest",
        "grpc",
        "backend",
        "server",
        "microservice",
    ],
    "devops": [
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "ci-cd",
        "terraform",
        "ansible",
        "github-actions",
        "jenkins",
        "devops",
        "cloud",
        "linux",
        "ubuntu",
        "k8s",
        "bash",
        "deploy",
        "nginx",
    ],
    "database": [
        "sql",
        "mysql",
        "postgres",
        "mongo",
        "redis",
        "database",
        "schema",
        "prisma",
        "orm",
        "nosql",
        "supabase",
        "neon",
        "sqlite",
    ],
    "design": [
        "ui",
        "ux",
        "design",
        "figma",
        "avatar",
        "background-removal",
        "svg",
        "animation",
        "motion",
        "framer",
        "photoshop",
        "illustrator",
        "creative",
        "taste",
        "requirements-clarity",
    ],
    "automation": [
        "automation",
        "zapier",
        "make",
        "n8n",
        "selenium",
        "playwright",
        "puppeteer",
        "bot",
        "workflow",
        "scraper",
        "cron",
    ],
    "mobile": [
        "ios",
        "android",
        "react-native",
        "flutter",
        "swift",
        "kotlin",
        "mobile",
        "xcode",
    ],
    "game-dev": [
        "game-dev",
        "gamedev",
        "unity",
        "unreal",
        "godot",
        "phaser",
        "raylib",
        "pygame",
    ],
    "business": [
        "business",
        "founder",
        "sales",
        "marketing",
        "seo",
        "growth",
        "product",
        "agile",
        "scrum",
        "jira",
        "b2b",
        "crm",
        "cro",
        "onboarding",
        "pricing",
        "launch",
        "referral",
        "paywall",
    ],
    "writing": [
        "writing",
        "copywriting",
        "blog",
        "documentation",
        "readme",
        "readmes",
        "study",
        "teardown",
        "content",
        "journalism",
        "copy-editing",
        "humanizer",
    ],
    "3d-graphics": [
        "blender",
        "threejs",
        "three-js",
        "webgl",
        "rendering",
        "mesh",
        "texture",
        "shader",
    ],
    "aerospace": [
        "satellite",
        "orbit",
        "space",
        "aerodynamics",
        "avionic",
        "spacecraft",
    ],
    "agents": [
        "multi-agent",
        "swarm",
        "autonomous",
        "orchestration",
        "autogen",
        "crewai",
    ],
    "animation": [
        "gsap",
        "lottie",
        "keyframe",
        "tween",
        "rigging",
        "theatre-js",
    ],
    "architecture": [
        "architecture",
        "clean-code",
        "system-design",
        "ddd",
        "architect",
        "c4-architecture",
        "composition-patterns",
    ],
    "biomedical": [
        "dna",
        "protein",
        "medical",
        "health",
        "genomics",
        "bioinfo",
        "clinical",
    ],
    "blockchain": [
        "crypto",
        "web3",
        "solidity",
        "smart-contract",
        "ethereum",
        "bitcoin",
        "nft",
        "staking",
    ],
    "compliance": [
        "gdpr",
        "hipaa",
        "soc2",
        "audit",
        "policy",
        "legal",
        "privacy",
    ],
    "data-science": [
        "pandas",
        "numpy",
        "matplotlib",
        "scikit",
        "jupyter",
        "visualization",
        "etl",
    ],
    "education": [
        "learning",
        "course",
        "tutor",
        "student",
        "curriculum",
        "teaching",
        "university",
    ],
    "finance": [
        "trading",
        "stock",
        "portfolio",
        "banking",
        "ledger",
        "investment",
        "fintech",
    ],
    "marketing": [
        "ads",
        "campaign",
        "social-media",
        "brand",
        "analytics",
        "funnel",
        "email-marketing",
        "paid-ads",
    ],
    "mcp": [
        "mcp",
        "model-context-protocol",
    ],
    "media-production": [
        "video",
        "audio",
        "podcast",
        "editing",
        "streaming",
        "ffmpeg",
        "obs",
    ],
    "programming": [
        "python",
        "javascript",
        "typescript",
        "java",
        "cpp",
        "ruby",
        "php",
        "csharp",
        "algorithm",
        "data-structure",
    ],
    "prompt-engineering": [
        "system-prompt",
        "few-shot",
        "chain-of-thought",
        "meta-prompt",
        "enhance-prompt",
    ],
    "quantum": [
        "qubit",
        "qiskit",
        "quantum",
        "superposition",
        "entanglement",
    ],
    "robotics": [
        "ros",
        "arduino",
        "raspberry",
        "hardware",
        "sensor",
        "firmware",
        "robot",
    ],
    "simulation": [
        "physics",
        "modeling",
        "digital-twin",
        "solver",
    ],
    "testing": [
        "test",
        "unit-test",
        "jest",
        "pytest",
        "cypress",
        "qa",
    ],
    "tooling": [
        "cli",
        "prettier",
        "eslint",
        "bundler",
        "npm",
        "pip",
        "extension",
        "plugin",
        "datadog",
        "mermaid",
        "draw-io",
        "excalidraw",
        "marp",
    ],
}


def print_banner():
    print(f"\n{Colors.BOLD}{Colors.CYAN}    🎯 SkillPointer {Colors.ENDC}")
    print(f"{Colors.BLUE}    Infinite Context. Zero Token Tax.\n{Colors.ENDC}")


def _keyword_matches(keyword: str, name_lower: str) -> bool:
    """Match a keyword against a skill name using word boundaries.

    This prevents false positives like "ar" matching inside "marketing"
    or "orm" matching inside "performance". Keywords are escaped and
    matched at word boundaries (\\b) in the normalized skill name.
    """
    escaped = re.escape(keyword)
    # Use word-boundary matching so "orm" won't match inside "performance"
    # but "orm" will match "my-orm-tool" (boundaries include hyphens via \\b)
    pattern = rf"(?:^|[-_ ])({escaped})(?:[-_ ]|$)"
    return bool(re.search(pattern, name_lower))


def get_category_for_skill(skill_name: str) -> str:
    # Normalize the name
    if skill_name.startswith('"') and skill_name.endswith('"'):
        name_lower = (
            skill_name[1:-1].strip().lower().replace("_", "-").replace(" ", "-")
        )
    else:
        name_lower = skill_name.lower().replace("_", "-")

    # Phase 1: Prefix overrides (highest priority, zero ambiguity)
    for prefix, category in PREFIX_OVERRIDES.items():
        if name_lower.startswith(prefix):
            return category

    # Phase 2: Special case — code review with PR terms
    has_pr_term = any(
        term in name_lower for term in ("pr-review", "pull-request", "merge-request")
    )
    if "review" in name_lower and has_pr_term:
        return "code-review"

    # Phase 3: Word-boundary heuristic matching
    for category, keywords in DOMAIN_HEURISTICS.items():
        for kw in keywords:
            if _keyword_matches(kw, name_lower):
                return category

    return "_uncategorized"


# ==========================================
# Interactive AI Classification
# ==========================================


def _get_cache_path() -> Path:
    """Return path to the classification cache file."""
    return CONFIG["hidden_library_dir"] / ".classifications.json"


def _load_classification_cache() -> dict:
    """Load cached AI classification decisions from disk."""
    cache_path = _get_cache_path()
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_classification_cache(cache: dict):
    """Persist AI classification decisions to disk."""
    cache_path = _get_cache_path()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _get_all_categories() -> list:
    """Return sorted list of all known category names from DOMAIN_HEURISTICS."""
    cats = sorted(DOMAIN_HEURISTICS.keys())
    if "_uncategorized" not in cats:
        cats.append("_uncategorized")
    return cats


def _read_skill_excerpt(skill_dir: Path, max_lines: int = 60) -> str:
    """Read the first N lines of a skill's SKILL.md for context."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "(no SKILL.md found)"
    try:
        lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
        excerpt = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            excerpt += f"\n... ({len(lines) - max_lines} more lines)"
        return excerpt
    except OSError:
        return "(could not read SKILL.md)"


def ask_ai_for_category(skill_name: str, skill_dir: Path, cache: dict) -> str:
    """Ask the AI agent to classify a skill interactively.

    Prints the skill content and available categories to stdout, then reads
    the AI's decision from stdin. The AI agent running this script sees the
    output and types the category name.

    Decisions are cached so re-runs don't re-ask.
    """
    # Check cache first
    if skill_name in cache:
        cached = cache[skill_name]
        if cached in _get_all_categories():
            return cached

    categories = _get_all_categories()
    excerpt = _read_skill_excerpt(skill_dir)

    # Print the prompt for the AI agent to see
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}🤖 CLASSIFY: {skill_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"\n{Colors.BLUE}SKILL.md excerpt:{Colors.ENDC}")
    print(f"{'─' * 40}")
    print(excerpt)
    print(f"{'─' * 40}")
    print(f"\n{Colors.BOLD}Available categories:{Colors.ENDC}")
    for i, cat in enumerate(categories, 1):
        print(f"  {i:2d}. {cat}")
    print(
        f"\n{Colors.WARNING}Type the category name (or number) for '{skill_name}':{Colors.ENDC}"
    )

    # Read the AI's answer
    try:
        answer = input("> ").strip().lower().replace(" ", "-")
    except (EOFError, KeyboardInterrupt):
        print(f"{Colors.WARNING}  Skipped → _uncategorized{Colors.ENDC}")
        return "_uncategorized"

    # Accept either a number or a category name
    if answer.isdigit():
        idx = int(answer) - 1
        if 0 <= idx < len(categories):
            chosen = categories[idx]
        else:
            print(f"{Colors.FAIL}  Invalid number → _uncategorized{Colors.ENDC}")
            chosen = "_uncategorized"
    elif answer in categories:
        chosen = answer
    else:
        # Fuzzy: check if the answer is a substring of exactly one category
        matches = [c for c in categories if answer in c]
        if len(matches) == 1:
            chosen = matches[0]
        else:
            print(
                f"{Colors.FAIL}  Unrecognized category '{answer}' → _uncategorized{Colors.ENDC}"
            )
            chosen = "_uncategorized"

    print(f"{Colors.GREEN}  ✓ Classified '{skill_name}' → {chosen}{Colors.ENDC}")

    # Cache the decision
    cache[skill_name] = chosen
    _save_classification_cache(cache)

    return chosen


def classify_skill(skill_name: str, skill_dir: Path = None, cache: dict = None) -> str:
    """Classify a skill using the configured method.

    classify_mode in CONFIG controls behavior:
      - "heuristic": keyword matching only (fast, offline)
      - "interactive": always ask the AI agent via stdin/stdout
      - "auto" (default): try heuristics first, ask AI only if result
        would be _uncategorized

    Returns the category string.
    """
    mode = CONFIG.get("classify_mode", "auto")

    if mode == "heuristic":
        return get_category_for_skill(skill_name)

    if mode == "interactive":
        if skill_dir and cache is not None:
            return ask_ai_for_category(skill_name, skill_dir, cache)
        return get_category_for_skill(skill_name)

    # mode == "auto": heuristic first, AI fallback for unknowns
    result = get_category_for_skill(skill_name)
    if result == "_uncategorized" and skill_dir and cache is not None:
        return ask_ai_for_category(skill_name, skill_dir, cache)
    return result


def setup_directories():
    agent_name = CONFIG["agent_name"]
    active_skills_dir = CONFIG["active_skills_dir"]
    hidden_library_dir = CONFIG["hidden_library_dir"]

    if not active_skills_dir.exists():
        print(
            f"{Colors.FAIL}✖ Error: {agent_name} skills directory not found at {active_skills_dir}{Colors.ENDC}"
        )
        print(
            f"{Colors.WARNING}Please ensure {agent_name} is installed and configured.{Colors.ENDC}"
        )
        return False

    hidden_library_dir.mkdir(parents=True, exist_ok=True)
    return True


def _migrate_directory(
    source_dir: Path,
    hidden_library_dir: Path,
    copy_only: bool = False,
    cache: dict = None,
):
    """Migrate skills from a single source directory into the hidden vault.

    Args:
        source_dir: Directory to scan for skill folders.
        hidden_library_dir: The hidden vault destination.
        copy_only: If True, copy instead of move (used for extra dirs we don't own).
        cache: Classification cache dict (passed to classify_skill for AI mode).

    Returns:
        Tuple of (category_counts dict, moved_count int).
    """
    category_counts = {}
    moved_count = 0

    if not source_dir.exists():
        return category_counts, moved_count

    for folder in list(source_dir.iterdir()):
        if not folder.is_dir():
            continue

        # Ignore existing pointers
        if folder.name.endswith("-category-pointer"):
            continue

        # Ignore empty folders
        if not any(folder.iterdir()):
            continue

        # Must have a SKILL.md to be a real skill
        if not (folder / "SKILL.md").exists():
            continue

        category = classify_skill(folder.name, folder, cache)
        cat_dir = hidden_library_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        dest = cat_dir / folder.name
        if dest.exists():
            shutil.rmtree(dest)

        if copy_only:
            shutil.copytree(str(folder), str(dest))
        else:
            shutil.move(str(folder), str(cat_dir))

        category_counts[category] = category_counts.get(category, 0) + 1
        moved_count += 1

    return category_counts, moved_count


def migrate_skills():
    active_skills_dir = CONFIG["active_skills_dir"]
    hidden_library_dir = CONFIG["hidden_library_dir"]
    extra_dirs = CONFIG.get("extra_skills_dirs", [])

    print(f"{Colors.BOLD}📦 Phase 1: Analyzing and Migrating Skills...{Colors.ENDC}\n")

    cache = _load_classification_cache()
    total_counts = {}
    total_moved = 0

    # Primary directory: move skills out
    counts, moved = _migrate_directory(
        active_skills_dir, hidden_library_dir, copy_only=False, cache=cache
    )
    for cat, n in counts.items():
        total_counts[cat] = total_counts.get(cat, 0) + n
    total_moved += moved

    # Extra directories: copy skills (we don't own these dirs, so leave originals)
    for extra_dir in extra_dirs:
        if not extra_dir.exists():
            continue
        print(f"{Colors.CYAN}  ↳ Scanning extra directory: {extra_dir}{Colors.ENDC}")
        counts, moved = _migrate_directory(
            extra_dir, hidden_library_dir, copy_only=True, cache=cache
        )
        for cat, n in counts.items():
            total_counts[cat] = total_counts.get(cat, 0) + n
        total_moved += moved

    # Print summary
    if total_moved > 0:
        for cat in sorted(total_counts.keys()):
            print(f"{Colors.GREEN}  ✓ {cat}: {total_counts[cat]} skill(s){Colors.ENDC}")

    print(
        f"\n{Colors.BLUE}✔ Successfully migrated {total_moved} raw skills into the hidden vault at {hidden_library_dir}{Colors.ENDC}\n"
    )
    return total_counts


def generate_pointers(category_counts):
    active_skills_dir = CONFIG["active_skills_dir"]
    hidden_library_dir = CONFIG["hidden_library_dir"]

    print(
        f"{Colors.BOLD}⚡ Phase 2: Generating Dynamic Category Pointers...{Colors.ENDC}\n"
    )

    pointer_template = """---
name: {category_name}-category-pointer
description: Triggers when encountering any task related to {category_name}. This is a pointer to a library of specialized skills.
---

# {category_title} Capability Library 🎯

You do not have all {category_title} skills loaded immediately in your background context. Instead, you have access to a rich library of {count} highly-specialized skills on your local filesystem.

## Instructions
1. When you need to perform a task related to {category_name}, you MUST use your file reading tools (like `list_dir` and `view_file` or `read_file`) to browse the hidden library directory: `{library_path}`
2. Locate the specific Markdown files related to the exact sub-task you need.
3. Read the relevant Markdown file(s) into your context.
4. Follow the specific instructions and best practices found within those files to complete the user's request.

## Available Knowledge
This library contains {count} specialized skills covering various aspects of {category_title}.

**Hidden Library Path:** `{library_path}`

*Reminder: Do not guess best practices or blindly search GitHub. Always consult your local library files first.*
"""

    created_pointers = 0
    total_skills_indexed = 0

    # We will scan the hidden_library_dir completely to ensure we include skills added previously or manually
    for cat_dir in hidden_library_dir.iterdir():
        if not cat_dir.is_dir():
            continue

        cat = cat_dir.name

        # Count actual SKILL.md files inside
        count = sum(1 for p in cat_dir.rglob("SKILL.md"))
        if count == 0:
            continue

        total_skills_indexed += count

        pointer_name = f"{cat}-category-pointer"
        pointer_dir = active_skills_dir / pointer_name
        pointer_dir.mkdir(parents=True, exist_ok=True)

        cat_title = cat.replace("-", " ").title()

        content = pointer_template.format(
            category_name=cat,
            category_title=cat_title,
            count=count,
            library_path=str(cat_dir.absolute()).replace(
                "\\", "/"
            ),  # Ensure cross-platform path format in markdown
        )

        with open(pointer_dir / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(content)

        created_pointers += 1
        print(
            f"{Colors.CYAN}  ⊕ Created {pointer_name} ➔ Indexes {count} skills.{Colors.ENDC}"
        )

    print(
        f"\n{Colors.BLUE}✔ Successfully generated {created_pointers} ultra-lightweight pointers indexing {total_skills_indexed} total skills.{Colors.ENDC}"
    )


def watch_for_new_skills(interval: int = 10):
    """Poll skills directories and auto-migrate new skills as they appear.

    Watches the primary active_skills_dir and all extra_skills_dirs. When a
    new non-pointer skill folder with a SKILL.md is detected, it's immediately
    classified (using the configured classify_mode) and migrated into the vault.
    Pointers are regenerated after each batch of new skills.
    """
    active_skills_dir = CONFIG["active_skills_dir"]
    hidden_library_dir = CONFIG["hidden_library_dir"]
    extra_dirs = CONFIG.get("extra_skills_dirs", [])

    all_dirs = [active_skills_dir] + [d for d in extra_dirs if d.exists()]
    cache = _load_classification_cache()

    print(
        f"{Colors.BOLD}{Colors.CYAN}👁  Watch mode active (polling every {interval}s){Colors.ENDC}"
    )
    print(
        f"{Colors.BLUE}   Monitoring: {', '.join(str(d) for d in all_dirs)}{Colors.ENDC}"
    )
    print(f"{Colors.BLUE}   Press Ctrl+C to stop.{Colors.ENDC}\n")

    # Build initial snapshot of known skills in the vault
    known_vault_skills = set()
    if hidden_library_dir.exists():
        for cat_dir in hidden_library_dir.iterdir():
            if cat_dir.is_dir():
                for skill_dir in cat_dir.iterdir():
                    if skill_dir.is_dir():
                        known_vault_skills.add(skill_dir.name)

    while True:
        try:
            new_found = False

            for scan_dir in all_dirs:
                if not scan_dir.exists():
                    continue
                is_extra = scan_dir != active_skills_dir

                for folder in scan_dir.iterdir():
                    if not folder.is_dir():
                        continue
                    if folder.name.endswith("-category-pointer"):
                        continue
                    if folder.name in known_vault_skills:
                        continue
                    if not (folder / "SKILL.md").exists():
                        continue

                    # New skill detected — classify it
                    category = classify_skill(folder.name, folder, cache)
                    cat_dir = hidden_library_dir / category
                    cat_dir.mkdir(parents=True, exist_ok=True)

                    dest = cat_dir / folder.name
                    if dest.exists():
                        shutil.rmtree(dest)

                    if is_extra:
                        shutil.copytree(str(folder), str(dest))
                        action = "Copied"
                    else:
                        shutil.move(str(folder), str(cat_dir))
                        action = "Moved"

                    known_vault_skills.add(folder.name)
                    new_found = True
                    print(
                        f"{Colors.GREEN}  ⚡ {action} new skill '{folder.name}' ➔ {category}/{Colors.ENDC}"
                    )

            if new_found:
                # Regenerate pointers to include the new skills
                generate_pointers({})
                print()

            time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Watch mode stopped.{Colors.ENDC}")
            break


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="SkillPointer Setup - Infinite Context. Zero Token Tax."
    )
    parser.add_argument(
        "--agent",
        choices=["opencode", "claude"],
        default="opencode",
        help="Target AI agent (opencode or claude)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for new skills and auto-migrate them",
    )
    parser.add_argument(
        "--watch-interval",
        type=int,
        default=10,
        help="Polling interval in seconds for watch mode (default: 10)",
    )
    parser.add_argument(
        "--extra-dir",
        action="append",
        default=[],
        help="Additional skill directories to scan (can be repeated)",
    )
    parser.add_argument(
        "--classify",
        choices=["auto", "interactive", "heuristic"],
        default="auto",
        help=(
            "How to categorize skills. "
            "'heuristic' = keyword matching only (fast, offline). "
            "'interactive' = always ask the AI agent for every skill. "
            "'auto' (default) = try heuristics first, ask AI only for "
            "skills that would land in _uncategorized."
        ),
    )
    args, unknown = parser.parse_known_args()

    if args.agent == "claude":
        CONFIG["agent_name"] = "Claude Code"
        CONFIG["active_skills_dir"] = Path.home() / ".claude" / "skills"
        CONFIG["hidden_library_dir"] = Path.home() / ".skillpointer-vault"
        CONFIG["extra_skills_dirs"] = []

    # Set classification mode
    CONFIG["classify_mode"] = args.classify

    # Add any user-specified extra directories
    for extra in args.extra_dir:
        CONFIG["extra_skills_dirs"].append(Path(extra).expanduser())

    # Handle 'install' argument for compatibility with Install.bat/vbs
    if unknown and unknown[0:1] == ["install"]:
        pass

    print_banner()
    if not setup_directories():
        return

    time.sleep(1)
    category_counts = migrate_skills()
    time.sleep(1)
    generate_pointers(category_counts)

    print(
        f"\n{Colors.BOLD}{Colors.GREEN}=========================================={Colors.ENDC}"
    )
    print(
        f"{Colors.BOLD}{Colors.GREEN}✨ Setup Complete! Your AI is now optimized. ✨{Colors.ENDC}"
    )
    print(
        f"{Colors.BOLD}{Colors.GREEN}=========================================={Colors.ENDC}"
    )
    print(f"Your active skills directory now only contains optimized Pointers.")
    print(
        "When you prompt your AI, its context window will be completely empty, but it will dynamically fetch from your massive library exactly when needed."
    )

    if args.watch:
        print()
        watch_for_new_skills(interval=args.watch_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup cancelled by user.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
