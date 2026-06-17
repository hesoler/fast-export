# Repository Instructions

## Overview
`hg-fast-export` converts Mercurial repositories to Git using `git-fast-import`.

## Key Commands
- **Initial Conversion:**
  ```bash
  git init <repo-git>
  cd <repo-git>
  # -r: local mercurial repo path
  # -n: disable auto-sanitization (highly recommended for new conversions)
  hg-fast-export.sh -r <local-repo> -n
  git checkout
  ```
- **Incremental Import:** Run `hg-fast-export.sh -r <local-repo>` again in the same git repo.
- **Author/Branch/Tag Mapping:** Use `-A`, `-B`, `-T` with a mapping file (format: `"key"="value"`).

## Essential Quirks & Constraints
- **Requirements:** Python >=3.7, `mercurial` package (`pip install mercurial`).
- **No Remote Access:** `hg-fast-export` cannot access remote (http/ssh) repositories. **Always clone locally first.**
- **No Auto-Checkout:** The tool does not update the working directory. Run `git checkout` after the import.
- **Case Sensitivity:** On case-insensitive file systems (Windows/macOS), branch names differing only in case (e.g., `A` and `a`) will collide. Use mapping files to rename branches in these cases.
- **Branch Naming:** Built-in sanitization is often broken. Use `-n` for new conversions.
- **Plugins:** Use `--plugin <name>` to enable plugins from `plugins/` directory.
- **Storage:** Incremental imports create new pack files. Repack the repo often.
