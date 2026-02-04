---
name: parallel-worktrees
description: Run parallel OpenCode/Claude sessions safely using git worktrees.
license: MIT
compatibility: Requires git worktree support.
metadata:
  author: opencode
  version: "1.0"
  generatedBy: "manual"
---

Use git worktrees to isolate parallel sessions while sharing the same repo history.

---

## Goals

- Prevent file state collisions across parallel sessions.
- Keep branch history shared and easy to merge.
- Make cleanup explicit and safe.

---

## Workflow

### 1) Create a worktree per task

```bash
git worktree add -b feature/<task-name> ../<repo-name>-<task-name>
```

Or for an existing branch:

```bash
git worktree add ../<repo-name>-<task-name> <branch-name>
```

### 2) Start a session in each worktree

Open a new OpenCode/Claude session in each worktree directory.

### 3) Track worktrees

```bash
git worktree list
```

### 4) Remove finished worktrees

```bash
git worktree remove ../<repo-name>-<task-name>
```

---

## Best Practices

- Use descriptive worktree folder names matching task scope.
- One task per worktree; do not mix changes.
- Initialize dependencies per worktree (venv/npm/uv).
- Merge via PRs; delete feature branches after merge.

---

## Checklist

- [ ] One task per worktree
- [ ] Dependencies installed per worktree
- [ ] Worktree removed after merge
