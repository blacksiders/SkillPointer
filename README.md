# SkillPointer 🎯

**Infinite Context. Zero Token Tax.**

SkillPointer is a "Retrieval-Augmented Generation" (RAG) architectural pattern and utility script specifically designed for AI coding agents like [OpenCode](https://github.com/opencode-ai/opencode) and Claude Code. 

It solves the biggest problem with massive AI skill libraries: **Context Window Bloat**.

## The Problem: The "Token Tax"
Currently, when you install community skill packs (e.g., hundreds of animation principles, prompt engineering guides, or frontend best practices), your AI agent scans all of them and loads their descriptions into its background context window on *every single prompt*. 

If you have 1,000 skills, that requires thousands of tokens just for the AI to "remember" what it knows before it even reads your codebase. 
- It slows down the AI.
- It racks up your API costs.
- It distracts the AI during deep research modes (often causing timeouts or unrelated searches).

## The Solution: The Pointer Architecture
SkillPointer completely reorganizes your skill library:
1. **Hidden Storage:** It moves all of your raw skills into a completely hidden, isolated directory (e.g., `~/.opencode-skill-libraries/`). The AI's native scanner cannot see them here.
2. **Category Pointers:** It replaces those 1,000 skills with a handful (e.g., 10) lightweight "Pointer Skills" in your active directory (e.g., `web-dev-category-pointer`).
3. **Dynamic Retrieval:** When you ask a question, the AI only reads the 10 pointers. The pointer instructs the AI: *"I don't have the skills loaded, but you must use your command-line tools to read the hidden library folder and find the exact file you need first."*

**The result?** The AI can access 10,000+ skills instantaneously, but its background context is essentially zero.

## 🚀 Installation & Setup

We have provided an automated Python script that will instantly convert your existing, bloated skills directory into a blazingly fast Hierarchical Pointer Architecture.

### Step 1: Run the Refactor Script
Download and run the provided `setup.py` script. 

*Note: The script currently expects your active skills to be in `~/.config/opencode/skills` and will create the hidden library at `~/.opencode-skill-libraries`.*

```bash
python setup.py
```

### Step 2: Test It Out!
Start your AI agent and ask it to fetch a specific skill. For example:
> *"I want to create a CSS button. Please consult your `web-dev-category-pointer` skill first to find the exact best practice from your library before writing the code."*

Watch the execution logs:
1. The AI triggers the pointer.
2. The AI uses its native `list_dir` to browse the hidden folder.
3. The AI reads *only* the specific markdown file it needs.
4. It generates perfect code.

## Manual Implementation Example
If you prefer to set this up manually, we have provided templates in the `/examples` folder. You will need:
1. A hidden library directory (e.g., `~/.opencode-skill-libraries/animation`)
2. Your actual markdown skills placed inside that hidden directory.
3. A `SKILL.md` Pointer File inside your active `~/.config/opencode/skills/animation-category-pointer/` directory that tells the AI where to look.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=blacksiders/SkillPointer&type=Date)](https://star-history.com/#blacksiders/SkillPointer&Date)

---

*Open-sourced to optimize AI environments for developers everywhere. Built by breaking the limits of agentic workflows.*
