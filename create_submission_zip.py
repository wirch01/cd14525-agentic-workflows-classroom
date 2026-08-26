"""Rebuild the project submission zip with the current versions of its files.

Reads the file list from the original submission archive, resolves each entry
against the live sources in project/starter/, and writes a new archive
containing the same file set with up-to-date content. The original zip is
left untouched.
"""

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = REPO_ROOT / "project" / "starter"
ORIGINAL_ZIP = REPO_ROOT / (
    "Walter_Wirch-Project_AI-Powered_Agentic_Workflow_for_Project Management.zip"
)
NEW_ZIP = REPO_ROOT / (
    "Walter_Wirch-Project_AI-Powered_Agentic_Workflow_for_Project Management-updated.zip"
)


def main() -> int:
    if not ORIGINAL_ZIP.exists():
        print(f"ERROR: original archive not found: {ORIGINAL_ZIP}")
        return 1

    with zipfile.ZipFile(ORIGINAL_ZIP) as zf:
        entries = zf.namelist()

    missing = []
    updated = []
    unchanged = []

    with zipfile.ZipFile(NEW_ZIP, "w", zipfile.ZIP_DEFLATED) as out:
        with zipfile.ZipFile(ORIGINAL_ZIP) as orig:
            for name in entries:
                if name.endswith("/"):  # directory entry
                    out.writestr(name, b"")
                    continue

                source = SOURCE_ROOT / name
                if not source.exists():
                    missing.append(name)
                    continue

                new_bytes = source.read_bytes()
                old_bytes = orig.read(name)
                out.write(source, arcname=name)
                (updated if new_bytes != old_bytes else unchanged).append(name)

    print(f"Created: {NEW_ZIP.name}")
    print(f"\nUpdated files ({len(updated)}):")
    for name in updated:
        print(f"  * {name}")
    print(f"\nUnchanged files ({len(unchanged)}):")
    for name in unchanged:
        print(f"  - {name}")
    if missing:
        print(f"\nWARNING - files in the original zip but missing on disk ({len(missing)}):")
        for name in missing:
            print(f"  ! {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
