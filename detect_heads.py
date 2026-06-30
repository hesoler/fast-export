import sys

from mercurial import hg, ui

# Ruta al repositorio (pasada como argumento de línea de comandos)
repo_path = b""
if len(sys.argv) > 1:
    repo_path = sys.argv[1].encode('utf-8')
else:
    print("Error: Se debe proporcionar la ruta del repositorio como argumento.", file=sys.stderr)
    sys.exit(1)
u = ui.ui()
# Ensure we use unfiltered repo to see all heads including closed ones
repo = hg.repository(u, repo_path).unfiltered()


# Helper to find all ancestors of a revision
def get_ancestors(repo, rev):
    ancs = set()
    stack = [rev]
    while stack:
        r = stack.pop()
        if r in ancs:
            continue
        ancs.add(r)
        parents = [p for p in repo.changelog.parentrevs(r) if p != -1]
        stack.extend(parents)
    return ancs


branch_map = repo.branchmap()
print("# Generated head2branch plugins:")

# We want to identify branches with more than one head
# Iterate over branch names
for branch_name in branch_map:
    heads = branch_map.branchheads(branch_name, closed=True)

    if len(heads) > 1:
        # Sort heads by revision number to identify the primary one (highest rev)
        sorted_heads = sorted(heads, key=lambda h: repo.changelog.rev(h))
        primary_head = sorted_heads[-1]
        unnamed_heads = sorted_heads[:-1]

        # DEBUG: Imprimir qué cabeceras se consideran "sin nombre"
        print(f"# DEBUG: Branch {branch_name} primary: {repo.changelog.rev(primary_head)}, unnamed: {[repo.changelog.rev(h) for h in unnamed_heads]}", file=sys.stderr)

        # Get all ancestors
        primary_rev = repo.changelog.rev(primary_head)
        primary_ancs = get_ancestors(repo, primary_rev)

        for unnamed_head in unnamed_heads:
            # Get all ancestors of the unnamed head
            unnamed_rev = repo.changelog.rev(unnamed_head)
            unnamed_ancs = get_ancestors(repo, unnamed_rev)

            # Find commits that are part of the unnamed head but not the primary one
            divergent_set = unnamed_ancs - primary_ancs

            # IMPORTANT CHANGE: If divergent_set is empty, it means the head is a direct descendant 
            # of the primary branch, and needs to be renamed anyway if we want a branch.
            # So, if divergent_set is empty, we use the unnamed_head itself as the root.

            if not divergent_set:
                roots = [unnamed_rev]
            else:
                # Find the roots of the divergent set (first divergent commits)
                # roots are commits in divergent_set whose parents are NOT in divergent_set
                roots = []
                for rev in divergent_set:
                    parents = repo.changelog.parentrevs(rev)
                    # Filter out nullrev (-1)
                    parents = [p for p in parents if p != -1]
                    if not any(p in divergent_set for p in parents):
                        roots.append(rev)

            for root in roots:
                # 'root' is already the revision number (int), not a node hash
                root_rev = root
                # To get the node hash, we use repo.changelog.node(root)
                node = repo.changelog.node(root)
                root_hex = node.hex()
                if isinstance(root_hex, bytes):
                    root_hex = root_hex.decode('utf-8')

                branch_name_str = branch_name.decode('utf-8', 'replace')
                # Generate a unique branch name for git - including revision number
                clean_branch = branch_name_str.replace(" ", "_")
                new_branch = f"{clean_branch}-unnamed-head-{root_rev}"

                # Print the plugin argument
                plugin_str = f"--plugin head2branch={new_branch},{root_hex}\n"
                sys.stdout.buffer.write(plugin_str.encode('utf-8'))
