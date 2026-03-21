# CLAUDE.md - Development Guide for St Repository

This document provides comprehensive guidance for Claude AI assistants and developers working on the **St** repository. It outlines the codebase structure, development workflows, and key conventions to follow.

---

## 1. Repository Overview

**Project Name:** St
**Purpose:** [To be defined by the team]
**Organization:** sertantoktas-ui
**Remote:** http://local_proxy@127.0.0.1:46297/git/sertantoktas-ui/St

### Current State
- **Branches:**
  - `main` - Production branch
  - `master` - Legacy/alternative primary branch
  - `claude/*` - Feature branches for Claude-assisted development
- **Files:** Minimal initial setup (README.md only)
- **Status:** Early-stage project

---

## 2. Codebase Structure

```
St/
├── README.md           # Project overview and basic information
├── CLAUDE.md           # This file - AI assistant development guide
├── .git/               # Git repository metadata
├── src/                # (To be created) Source code directory
├── tests/              # (To be created) Test files
├── docs/               # (To be created) Documentation
└── [config files]      # (To be created) Package configs, CI/CD, etc.
```

### Directory Guidelines

When expanding the codebase, follow these conventions:

- **`src/`** - All application source code
  - Organize by feature or domain
  - Use clear, descriptive names

- **`tests/`** - Test suites
  - Mirror `src/` structure
  - Maintain >80% code coverage goal

- **`docs/`** - Documentation
  - Architecture decisions (ADRs)
  - Setup guides
  - API documentation

- **Config Files** - Repository root
  - `.gitignore` - Git exclusions
  - `.editorconfig` - Editor settings
  - Package/build configs (`package.json`, `tsconfig.json`, etc.)
  - CI/CD configs (`.github/workflows/`, etc.)

---

## 3. Git Workflow & Branching Strategy

### Branch Naming Convention

All branches must follow this pattern:
```
<type>/<description>-<session-id>
```

**Types:**
- `claude/` - Feature branches developed with Claude AI assistance
- `feature/` - Standard feature branches
- `bugfix/` - Bug fix branches
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

**Example:** `claude/add-claude-documentation-6v0WD`

### Current Development Branch

**Active Branch:** `claude/add-claude-documentation-6v0WD`

All Claude-assisted development happens on this branch. Do NOT push to different branches without explicit permission.

### Git Operations

#### Creating a New Branch
```bash
git fetch origin <branch-name>    # Fetch the specific branch
git checkout <branch-name>        # Switch to it (creates locally if needed)
```

#### Committing Changes
```bash
git add <files>
git commit -m "Clear, descriptive commit message"
```

**Commit Message Format:**
```
<type>: <description>

<optional detailed explanation>

https://claude.ai/code/session_<SESSION_ID>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/dependency changes

#### Pushing Changes
```bash
git push -u origin <branch-name>
```

**CRITICAL:**
- Always use `-u origin` flag to set upstream tracking
- Branch name must start with `claude/` and end with session ID
- Push will fail with 403 if branch format is incorrect
- Retry failed pushes with exponential backoff: 2s, 4s, 8s, 16s

#### Pulling Changes
```bash
git pull origin <branch-name>
# Or for safer pulls:
git fetch origin <branch-name>
git merge origin/<branch-name>
```

### Commit Strategy
- Make **atomic commits** - one logical change per commit
- Commit early and often
- Always include session URL in commit messages for traceability
- Never force-push to shared branches without authorization
- Review diffs before committing (`git diff`, `git diff --staged`)

---

## 4. Development Workflow

### Starting Work
1. Ensure you're on the correct branch: `git checkout claude/add-claude-documentation-6v0WD`
2. Fetch latest: `git fetch origin`
3. Verify working directory is clean: `git status`
4. Create/switch to your feature branch if needed

### During Development
1. **Edit files** - Make changes to implement features or fixes
2. **Test locally** - Run tests and verification before committing (when applicable)
3. **Commit regularly** - Create atomic commits with clear messages
4. **Push periodically** - Keep remote branch updated
5. **Review changes** - Use `git diff` to verify before committing

### Completing Work
1. Ensure all changes are committed
2. Push final changes: `git push -u origin <branch-name>`
3. Create pull request (if applicable)
4. Update CLAUDE.md if adding new conventions or patterns
5. Notify team of completion

### Key Principles
- **Work incrementally** - Don't attempt massive refactors without planning
- **Test before committing** - Verify functionality works
- **Document as you go** - Update README.md, CLAUDE.md, and code comments
- **Keep commits focused** - One feature/fix per commit when possible
- **Communicate changes** - Use clear commit messages and PR descriptions

---

## 5. AI Assistant Conventions

### Before Making Changes

1. **Read the codebase** - Use Read tool for relevant files before editing
2. **Understand context** - Ask questions if requirements are unclear
3. **Plan changes** - Use TodoWrite for multi-step tasks
4. **Confirm decisions** - Use AskUserQuestion for architectural choices

### Code Quality Standards

- **No security vulnerabilities** - Avoid command injection, XSS, SQL injection (OWASP Top 10)
- **Avoid over-engineering** - Keep solutions simple and focused
- **Don't add unnecessary features** - Stick to requirements
- **Don't premature abstractions** - Wait for 3+ uses before creating utilities
- **Trust framework guarantees** - Only validate at system boundaries (user input, external APIs)
- **Keep code focused** - One responsibility per module/function

### When to Use Tools

- **Read** - For reading files (NOT `cat`, `head`, `tail`)
- **Edit** - For modifying existing files (NOT `sed`, `awk`)
- **Write** - For creating new files (NOT `echo`, `cat <<EOF`)
- **Glob** - For file pattern matching (NOT `find`, `ls`)
- **Grep** - For content search (NOT `grep`, `rg` bash commands)
- **Bash** - For system commands, only when no dedicated tool fits
- **Agent** - For complex multi-step tasks requiring research
- **TodoWrite** - For tracking multi-step work items
- **AskUserQuestion** - When clarification or decisions are needed

### Git Discipline

- **No force-push to shared branches** without explicit authorization
- **No skipping hooks** (--no-verify) unless user explicitly requests
- **Create NEW commits** after hook failures (don't amend)
- **Review changes** before committing (`git diff`)
- **Avoid uncommitted deletions** - Investigate before removing
- **No git reset --hard** without explicit approval

### Documentation Standards

- Update README.md when adding significant features
- Add/update CLAUDE.md when establishing new conventions
- Include code comments only where logic isn't self-evident
- Keep documentation in sync with code changes

---

## 6. File Editing Rules

### Edit Tool Usage

The **Edit** tool should be used for all file modifications:
- Preserves exact indentation (tabs/spaces)
- Shows clear diffs for review
- Prevents accidental file corruption

**Rule:** You must use the Read tool at least once before editing a file.

### Write Tool Usage

The **Write** tool creates new files or completely rewrites existing ones:
- Use only when creating new files
- Use sparingly - prefer Edit for modifications
- Don't create unnecessary files

### Common File Types

- **Markdown (.md)** - Only create when explicitly requested
- **Configuration** - Follow project conventions
- **Source code** - Follow language and project conventions
- **Tests** - Match existing test structure and naming

---

## 7. Testing & Validation

### General Principles
- Write tests for new features
- Maintain or improve code coverage
- Run tests before committing
- Document test procedures

### Running Tests
```bash
# When test infrastructure exists, commands will be documented here
```

### Code Review
- Review diffs before committing: `git diff`
- Verify staged changes: `git diff --staged`
- Check commit messages match conventions
- Ensure no secrets or sensitive data in commits

---

## 8. Common Tasks

### Adding a New Feature
1. Create descriptive feature branch: `git checkout -b feature/description`
2. Plan with TodoWrite
3. Implement feature incrementally
4. Test thoroughly
5. Commit with clear messages
6. Push and open PR if applicable
7. Update CLAUDE.md if establishing new patterns

### Fixing a Bug
1. Create bugfix branch: `git checkout -b bugfix/issue-description`
2. Identify root cause by reading relevant code
3. Create minimal fix
4. Test the fix
5. Commit with reference to bug tracking system
6. Push and notify team

### Updating Documentation
1. Edit relevant .md files
2. Keep documentation in sync with code
3. Commit with type: `docs: <description>`
4. Include session URL in commit message

### Code Refactoring
1. Ensure tests pass before refactoring
2. Make small, focused changes
3. Run tests after each logical change
4. Commit with type: `refactor: <description>`
5. Don't combine refactoring with feature work

### Updating CLAUDE.md
1. When adding new conventions or patterns
2. When changing git workflow or branch strategy
3. When updating development procedures
4. Keep it current with actual practices

---

## 9. Important Principles & Constraints

### Safety First
- Never push to main/master without explicit approval
- Always use `-u origin <branch-name>` flag for first push
- No destructive operations without confirmation
- Investigate unexpected files/branches before deletion

### Respect Reversibility
- Local file edits are freely reversible
- Test changes before final push
- Get confirmation before:
  - Force-pushing
  - Deleting branches or files
  - Modifying CI/CD pipelines
  - Removing dependencies
  - Making public/shared changes

### Clear Communication
- Use descriptive commit messages
- Include session URL in commits
- Update CLAUDE.md for new patterns
- Ask questions before making assumptions
- Confirm ambiguous requirements

### Code Ownership
- Understand code before modifying
- Fix bugs, don't work around them
- Keep changes focused and minimal
- Don't refactor unnecessarily

---

## 10. Resources & Getting Help

### Repository Information
- **Remote URL:** http://local_proxy@127.0.0.1:46297/git/sertantoktas-ui/St
- **Current Branch:** claude/add-claude-documentation-6v0WD
- **Status:** Early-stage development

### Git Troubleshooting
- Push failed? Check branch name starts with 'claude/' and ends with session ID
- Network error? Retry with exponential backoff (2s, 4s, 8s, 16s)
- Merge conflicts? Resolve manually, don't discard changes

### Claude Code Help
- Type `/help` for Claude Code documentation
- Report issues: https://github.com/anthropics/claude-code/issues

### For Users
- Provide feedback on AI-assisted development
- Report any unclear conventions
- Suggest improvements to this guide

---

## 11. Project-Specific Notes

### Current State
- Fresh project with minimal initial setup
- No dependencies or build system yet
- README.md contains basic project info

### Next Steps (Recommended)
1. Define project purpose and scope
2. Set up package/build system (if applicable)
3. Create directory structure (src/, tests/, docs/)
4. Establish CI/CD pipeline
5. Add initial tests and documentation
6. Update README.md with detailed project info

### Team Conventions (To Be Established)
- Language/framework choice
- Code style guide (linter config)
- Testing framework and requirements
- Documentation standards
- Code review process

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-03-21 | Initial CLAUDE.md creation | Claude AI |
| | Added git workflow, conventions, and best practices | |
| | Documented AI assistant guidelines | |

---

**Last Updated:** 2026-03-21
**Version:** 1.0
**Maintainers:** Development Team
