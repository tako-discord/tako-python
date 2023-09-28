# Inspired by: https://github.com/Rapptz/RoboDanny/blob/rewrite/launcher.py#L118-L133
import os
import re
import datetime


def main(reason: str, kind: str = "V"):
    version = 0
    cwd = os.getcwd()
    path = os.path.join(cwd, "migrations") if not cwd.endswith("migrations") else cwd

    for file in os.listdir(path):
        if file.endswith(".sql"):
            tmp_version = int(file.split("V")[1][:1])
            if tmp_version > version:
                version = tmp_version + 1
    cleaned = re.sub(r"\s", "_", reason if reason else "").lower()
    filename = f"{kind}{version}{'__' if reason else ''}{cleaned}.sql"
    path = os.path.join(path, filename)

    stub = (
        f"-- Revises: V{version}\n"
        f"-- Creation Date: {datetime.datetime.utcnow()} UTC\n"
        f"-- Reason: {reason if reason else 'None'}\n\n"
    )

    with open(path, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(stub)


if __name__ == "__main__":
    input = input("Reason: ")
    main(input)
