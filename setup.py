#!/usr/bin/env python3
"""
SkillPointer - Infinite AI Context. Zero Token Tax.

A tool that reorganizes AI agent skills into a hierarchical pointer architecture
to minimize startup token costs while maintaining full skill accessibility.
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__version__ = "1.1.0"
__all__ = ["main", "get_category_for_skill"]

# ==========================================
# Constants
# ==========================================

PROGRESS_LOG_THRESHOLD = 5
BATCH_PROGRESS_INTERVAL = 50


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


# ==========================================
# Configuration
# ==========================================


@dataclass
class Config:
    """Runtime configuration for SkillPointer."""

    agent_name: str = "OpenCode"
    active_skills_dir: Path = field(
        default_factory=lambda: Path.home() / ".config" / "opencode" / "skills"
    )
    hidden_library_dir: Path = field(
        default_factory=lambda: Path.home() / ".opencode-skill-libraries"
    )
    dry_run: bool = False

    def validate(self) -> bool:
        """Validate configuration paths exist and are directories."""
        return self.active_skills_dir.is_dir()


# ==========================================
# Domain Heuristics
# ==========================================

DOMAIN_HEURISTICS: dict[str, list[str]] = {
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
        "vibesec",
        "vibe-security",
    ],
    "code-review": [
        "code-review",
        "code review",
        "codereview",
        "requesting-code-review",
        "code-review-excellence",
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
        "tag",
        "release",
        "conventional-commits",
    ],
    "ai-ml": [
        "ai-",
        "ml-",
        "llm",
        "agent",
        "gpt",
        "claude",
        "gemini",
        "openai",
        "anthropic",
        "prompt",
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
        "go-",
        "rust-",
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
        "gitlab",
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
        "db-",
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
        "mobile-",
    ],
    "game-dev": [
        "game",
        "unity",
        "unreal",
        "godot",
        "phaser",
        "3d",
        "vr",
        "ar",
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
    ],
    "writing": [
        "writing",
        "copywriting",
        "blog",
        "documentation",
        "readme",
        "study",
        "teardown",
        "content",
        "journalism",
    ],
    "3d-graphics": [
        "blender",
        "threejs",
        "webgl",
        "rendering",
        "3d-",
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
        "chain",
        "autogen",
        "crewai",
    ],
    "animation": [
        "gsap",
        "lottie",
        "keyframe",
        "transition",
        "tween",
        "rigging",
    ],
    "architecture": [
        "pattern",
        "clean-code",
        "system-design",
        "solid-",
        "ddd",
        "architect",
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
        "data-",
        "etl",
    ],
    "debug": [
        "debug",
        "debugging",
        "breakpoint",
        "logger",
        "logging",
        "trace",
        "profiler",
        "profiling",
        "devtools",
        "inspector",
        "monitor",
        "troubleshoot",
        "diagnostic",
        "error-tracking",
        "sentry",
        "datadog",
        "newrelic",
        "bugtracking",
        "bug",
        "bug-hunter",
        "hunter",
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
    ],
    "mcp": [
        "mcp-",
        "model-context-protocol",
        "server-",
        "client-",
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
        "swift",
        "kotlin",
        "algorithm",
        "data-structure",
        "mago",
    ],
    "prompt-engineering": [
        "system-prompt",
        "few-shot",
        "chain-of-thought",
        "prompt-",
        "meta-prompt",
    ],
    "quantum": [
        "qubit",
        "qiskit",
        "quantum-",
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
        "sim-",
        "digital-twin",
        "solver",
    ],
    "testing": [
        "test-",
        "unit-test",
        "jest",
        "pytest",
        "cypress",
        "quality",
        "qa-",
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
        "find-skills",
    ],
    "documentation": [
        "documentation",
        "docstring",
        "doc-",
        "code-documenter",
        "documenter",
        "readme",
        "api-docs",
        "swagger",
        "openapi",
        "jsdoc",
        "sphinx",
    ],
    "wordpress": [
        "wordpress",
        "wp-",
        "generatepress",
        "generateblocks",
        "gutenberg",
        "woocommerce",
        "acf",
        "wp-cli",
    ],
}

# Precomputed keyword lookup for O(1) category matching
_KEYWORD_LOOKUP: dict[str, str] = {
    kw: cat for cat, kws in DOMAIN_HEURISTICS.items() for kw in kws
}


# ==========================================
# Core Functions
# ==========================================


def print_banner() -> None:
    """Display the SkillPointer banner."""
    print(
        f"\n{Colors.BOLD}{Colors.CYAN}    🎯 SkillPointer v{__version__}{Colors.ENDC}"
    )
    print(f"{Colors.BLUE}    Infinite Context. Zero Token Tax.\n{Colors.ENDC}")


def get_category_for_skill(skill_name: str) -> str:
    """
    Determine the category for a skill based on its name.

    Uses keyword matching against the DOMAIN_HEURISTICS dictionary.
    Supports exact matching (when name is wrapped in quotes) and
    substring matching (default).

    Args:
        skill_name: The name of the skill folder.

    Returns:
        The category name, or "_uncategorized" if no match found.
    """
    exact_match = False
    if skill_name.startswith('"') and skill_name.endswith('"'):
        exact_match = True
        name_lower = (
            skill_name[1:-1].strip().lower().replace("_", "-").replace(" ", "-")
        )
    else:
        name_lower = skill_name.lower().replace("_", "-")

    # Special handling for PR-related code reviews
    has_pr_term = any(
        term in name_lower for term in ("pr-review", "pull-request", "merge-request")
    )
    if "review" in name_lower and has_pr_term:
        return "code-review"

    if exact_match:
        # Exact match: the full term must be in our keyword lookup
        if name_lower in _KEYWORD_LOOKUP:
            return _KEYWORD_LOOKUP[name_lower]
    else:
        # Substring match: check if any keyword is contained in the name
        for keyword, category in _KEYWORD_LOOKUP.items():
            if keyword in name_lower:
                return category

    return "_uncategorized"


def setup_directories(config: Config) -> bool:
    """
    Validate and create necessary directories.

    Args:
        config: The runtime configuration.

    Returns:
        True if setup successful, False otherwise.
    """
    agent_name = config.agent_name
    active_skills_dir = config.active_skills_dir
    hidden_library_dir = config.hidden_library_dir

    if not active_skills_dir.exists():
        print(
            f"{Colors.FAIL}✖ Error: {agent_name} skills directory not found at {active_skills_dir}{Colors.ENDC}"
        )
        print(
            f"{Colors.WARNING}Please ensure {agent_name} is installed and configured.{Colors.ENDC}"
        )
        return False

    if not active_skills_dir.is_dir():
        print(
            f"{Colors.FAIL}✖ Error: {active_skills_dir} is not a directory.{Colors.ENDC}"
        )
        return False

    try:
        hidden_library_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(
            f"{Colors.FAIL}✖ Error: Permission denied creating vault at {hidden_library_dir}{Colors.ENDC}"
        )
        return False
    except OSError as e:
        print(
            f"{Colors.FAIL}✖ Error: Could not create vault directory: {e}{Colors.ENDC}"
        )
        return False

    return True


def migrate_skills(config: Config) -> dict[str, int]:
    """
    Move skills from active directory to categorized vault.

    Args:
        config: The runtime configuration.

    Returns:
        Dictionary mapping category names to counts of migrated skills.
    """
    active_skills_dir = config.active_skills_dir
    hidden_library_dir = config.hidden_library_dir
    dry_run = config.dry_run

    action = "Would migrate" if dry_run else "Migrating"
    print(f"{Colors.BOLD}📦 Phase 1: {action} Skills...{Colors.ENDC}\n")

    category_counts: dict[str, int] = {}
    moved_count = 0
    pointer_count = 0
    errors: list[str] = []

    # Snapshot directory listing to avoid modification during iteration
    try:
        folders = list(active_skills_dir.iterdir())
    except PermissionError:
        print(
            f"{Colors.FAIL}✖ Error: Permission denied reading {active_skills_dir}{Colors.ENDC}"
        )
        return category_counts

    for folder in folders:
        if not folder.is_dir():
            continue

        # Ignore existing pointers
        if folder.name.endswith("-category-pointer"):
            pointer_count += 1
            continue

        # Ignore empty folders (with error handling)
        try:
            if not any(folder.iterdir()):
                continue
        except PermissionError:
            print(
                f"{Colors.WARNING}⚠ Skipping {folder.name} (permission denied){Colors.ENDC}"
            )
            continue

        category = get_category_for_skill(folder.name)
        cat_dir = hidden_library_dir / category

        if not dry_run:
            try:
                cat_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                errors.append(f"Permission denied creating {cat_dir}")
                continue

        dest = cat_dir / folder.name

        if dest.exists():
            if dry_run:
                print(
                    f"{Colors.WARNING}  ⚠ Would replace existing: {dest}{Colors.ENDC}"
                )
            else:
                try:
                    if dest.is_symlink() or dest.is_file():
                        dest.unlink()
                    else:
                        shutil.rmtree(dest)
                except (OSError, PermissionError) as e:
                    errors.append(f"Could not remove {dest}: {e}")
                    continue

        if dry_run:
            print(
                f"{Colors.GREEN}  ↳ Would map '{folder.name}' ➔ {category}/{Colors.ENDC}"
            )
        else:
            try:
                shutil.move(str(folder), str(dest))
            except (OSError, shutil.Error) as e:
                errors.append(f"Could not move {folder.name}: {e}")
                continue

        category_counts[category] = category_counts.get(category, 0) + 1
        moved_count += 1

        # Progress logging
        if (
            moved_count <= PROGRESS_LOG_THRESHOLD
            or moved_count % BATCH_PROGRESS_INTERVAL == 0
        ):
            print(
                f"{Colors.GREEN}  ↳ Mapped '{folder.name}' ➔ {category}/{Colors.ENDC}"
            )

    if moved_count > PROGRESS_LOG_THRESHOLD:
        remaining = moved_count - PROGRESS_LOG_THRESHOLD
        if moved_count % BATCH_PROGRESS_INTERVAL != 0:
            print(
                f"{Colors.GREEN}  ...and {remaining} more skills safely migrated.{Colors.ENDC}"
            )

    if errors:
        print(f"\n{Colors.WARNING}⚠ Encountered {len(errors)} error(s):{Colors.ENDC}")
        for error in errors[:5]:
            print(f"{Colors.WARNING}  - {error}{Colors.ENDC}")
        if len(errors) > 5:
            print(
                f"{Colors.WARNING}  ...and {len(errors) - 5} more errors.{Colors.ENDC}"
            )

    if dry_run:
        print(
            f"\n{Colors.BLUE}✔ Would migrate {moved_count} skills to {hidden_library_dir}{Colors.ENDC}\n"
        )
    else:
        print(
            f"\n{Colors.BLUE}✔ Successfully migrated {moved_count} raw skills into the hidden vault at {hidden_library_dir}{Colors.ENDC}\n"
        )

    return category_counts


def generate_pointers(config: Config, category_counts: dict[str, int]) -> None:
    """
    Create category pointer skills in the active directory.

    Args:
        config: The runtime configuration.
        category_counts: Dictionary of category names to skill counts.
    """
    active_skills_dir = config.active_skills_dir
    hidden_library_dir = config.hidden_library_dir
    dry_run = config.dry_run

    action = "Would generate" if dry_run else "Generating"
    print(
        f"{Colors.BOLD}⚡ Phase 2: {action} Dynamic Category Pointers...{Colors.ENDC}\n"
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

    try:
        cat_dirs = list(hidden_library_dir.iterdir())
    except PermissionError:
        print(
            f"{Colors.FAIL}✖ Error: Permission denied reading {hidden_library_dir}{Colors.ENDC}"
        )
        return

    for cat_dir in cat_dirs:
        if not cat_dir.is_dir():
            continue

        cat = cat_dir.name

        # Count actual SKILL.md files inside
        try:
            count = sum(1 for _ in cat_dir.rglob("SKILL.md"))
        except PermissionError:
            print(f"{Colors.WARNING}⚠ Skipping {cat} (permission denied){Colors.ENDC}")
            continue

        if count == 0:
            continue

        total_skills_indexed += count

        pointer_name = f"{cat}-category-pointer"
        pointer_dir = active_skills_dir / pointer_name

        if dry_run:
            print(
                f"{Colors.CYAN}  ⊕ Would create {pointer_name} ➔ Indexes {count} skills.{Colors.ENDC}"
            )
            created_pointers += 1
            continue

        try:
            pointer_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(
                f"{Colors.WARNING}⚠ Could not create {pointer_dir} (permission denied){Colors.ENDC}"
            )
            continue

        cat_title = cat.replace("-", " ").title()

        content = pointer_template.format(
            category_name=cat,
            category_title=cat_title,
            count=count,
            library_path=cat_dir.absolute().as_posix(),
        )

        try:
            with open(pointer_dir / "SKILL.md", "w", encoding="utf-8") as f:
                f.write(content)
        except (OSError, PermissionError) as e:
            print(
                f"{Colors.WARNING}⚠ Could not write {pointer_dir / 'SKILL.md'}: {e}{Colors.ENDC}"
            )
            continue

        created_pointers += 1
        print(
            f"{Colors.CYAN}  ⊕ Created {pointer_name} ➔ Indexes {count} skills.{Colors.ENDC}"
        )

    if dry_run:
        print(
            f"\n{Colors.BLUE}✔ Would generate {created_pointers} pointers indexing {total_skills_indexed} total skills.{Colors.ENDC}"
        )
    else:
        print(
            f"\n{Colors.BLUE}✔ Successfully generated {created_pointers} ultra-lightweight pointers indexing {total_skills_indexed} total skills.{Colors.ENDC}"
        )


def parse_args(argv: list[str] | None = None) -> tuple[Config, list[str]]:
    """
    Parse command-line arguments and return configuration.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Tuple of (Config, unknown_args).
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="SkillPointer Setup - Infinite Context. Zero Token Tax.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --agent claude
  %(prog)s --skill-dir ~/.agents/skills --vault-dir ~/.skillpointer-vault
  %(prog)s --dry-run
        """,
    )
    parser.add_argument(
        "--agent",
        choices=["opencode", "claude"],
        default="opencode",
        help="Target AI agent (default: opencode)",
    )
    parser.add_argument(
        "--skill-dir",
        type=str,
        help="Directory to search for skills (overrides --agent default)",
    )
    parser.add_argument(
        "--vault-dir",
        type=str,
        help="Directory to move skills to when creating pointers (overrides --agent default)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"SkillPointer v{__version__}",
    )

    args, unknown = parser.parse_known_args(argv)

    config = Config()

    if args.agent == "claude":
        config.agent_name = "Claude Code"
        config.active_skills_dir = Path.home() / ".claude" / "skills"
        config.hidden_library_dir = Path.home() / ".skillpointer-vault"

    if args.skill_dir:
        skill_dir = Path(args.skill_dir).expanduser().resolve()
        if not skill_dir.exists():
            print(
                f"{Colors.FAIL}✖ Error: --skill-dir path does not exist: {skill_dir}{Colors.ENDC}"
            )
            sys.exit(1)
        if not skill_dir.is_dir():
            print(
                f"{Colors.FAIL}✖ Error: --skill-dir is not a directory: {skill_dir}{Colors.ENDC}"
            )
            sys.exit(1)
        config.active_skills_dir = skill_dir

    if args.vault_dir:
        vault_dir = Path(args.vault_dir).expanduser().resolve()
        config.hidden_library_dir = vault_dir

    if args.dry_run:
        config.dry_run = True

    return config, unknown


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for SkillPointer.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    config, unknown = parse_args(argv)

    # Handle 'install' argument for compatibility with Install.bat/vbs
    if unknown and len(unknown) > 0 and unknown[0] == "install":
        pass

    if config.dry_run:
        print(
            f"{Colors.WARNING}🔍 DRY RUN MODE - No changes will be made{Colors.ENDC}\n"
        )

    print_banner()

    if not setup_directories(config):
        return 1

    category_counts = migrate_skills(config)
    generate_pointers(config, category_counts)

    print(
        f"\n{Colors.BOLD}{Colors.GREEN}=========================================={Colors.ENDC}"
    )
    if config.dry_run:
        print(f"{Colors.BOLD}{Colors.GREEN}✨ Dry Run Complete! ✨{Colors.ENDC}")
        print(
            f"{Colors.BOLD}{Colors.GREEN}=========================================={Colors.ENDC}"
        )
        print("Run without --dry-run to apply these changes.")
    else:
        print(
            f"{Colors.BOLD}{Colors.GREEN}✨ Setup Complete! Your AI is now optimized. ✨{Colors.ENDC}"
        )
        print(
            f"{Colors.BOLD}{Colors.GREEN}=========================================={Colors.ENDC}"
        )
        print("Your active skills directory now only contains optimized Pointers.")
        print(
            "When you prompt your AI, its context window will be completely empty, "
            "but it will dynamically fetch from your massive library exactly when needed."
        )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup cancelled by user.{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        sys.exit(1)
