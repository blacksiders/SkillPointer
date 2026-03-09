import os
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
}

# Advanced Heuristic Engine for Universal Categorization
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
    ],
}


def print_banner():
    print(f"\n{Colors.BOLD}{Colors.CYAN}    🎯 SkillPointer {Colors.ENDC}")
    print(f"{Colors.BLUE}    Infinite Context. Zero Token Tax.\n{Colors.ENDC}")


def get_category_for_skill(skill_name: str) -> str:
    # Detect exact search within quotes
    exact_match = False
    if skill_name.startswith('"') and skill_name.endswith('"'):
        exact_match = True
        name_lower = skill_name[1:-1].strip().lower().replace("_", "-").replace(" ", "-")
    else:
        name_lower = skill_name.lower().replace("_", "-")

    has_pr_term = any(
        term in name_lower for term in ("pr-review", "pull-request", "merge-request")
    )
    if "review" in name_lower and has_pr_term:
        return "code-review"

    for category, keywords in DOMAIN_HEURISTICS.items():
        if exact_match:
            # Exact match: the full term must match one of the keywords
            if name_lower in keywords:
                return category
        else:
            # Substring match: a known keyword is contained within the term
            if any(kw in name_lower for kw in keywords):
                return category
    return "_uncategorized"


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


def migrate_skills():
    active_skills_dir = CONFIG["active_skills_dir"]
    hidden_library_dir = CONFIG["hidden_library_dir"]

    print(f"{Colors.BOLD}📦 Phase 1: Analyzing and Migrating Skills...{Colors.ENDC}\n")

    category_counts = {}
    moved_count = 0
    pointer_count = 0

    for folder in list(active_skills_dir.iterdir()):
        if not folder.is_dir():
            continue

        # Ignore existing pointers
        if folder.name.endswith("-category-pointer"):
            pointer_count += 1
            continue

        # Ignore empty folders
        if not any(folder.iterdir()):
            continue

        category = get_category_for_skill(folder.name)
        cat_dir = hidden_library_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        dest = cat_dir / folder.name
        if dest.exists():
            shutil.rmtree(dest)

        shutil.move(str(folder), str(cat_dir))

        category_counts[category] = category_counts.get(category, 0) + 1
        moved_count += 1

        # Visually print a few for effect, but not all to avoid spam
        if moved_count <= 5 or moved_count % 50 == 0:
            print(
                f"{Colors.GREEN}  ↳ Mapped '{folder.name}' ➔ {category}/{Colors.ENDC}"
            )

    if moved_count > 5:
        print(
            f"{Colors.GREEN}  ...and {moved_count - 5} more skills safely migrated.{Colors.ENDC}"
        )

    print(
        f"\n{Colors.BLUE}✔ Successfully migrated {moved_count} raw skills into the hidden vault at {hidden_library_dir}{Colors.ENDC}\n"
    )
    return category_counts


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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SkillPointer Setup - Infinite Context. Zero Token Tax.")
    parser.add_argument("--agent", choices=["opencode", "claude"], default="opencode", 
                        help="Target AI agent (opencode or claude)")
    args, unknown = parser.parse_known_args()

    if args.agent == "claude":
        CONFIG["agent_name"] = "Claude Code"
        CONFIG["active_skills_dir"] = Path.home() / ".claude" / "skills"
        CONFIG["hidden_library_dir"] = Path.home() / ".skillpointer-vault"

    # Handle 'install' argument for compatibility with Install.bat/vbs
    if unknown and unknown[0] == "install":
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup cancelled by user.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
