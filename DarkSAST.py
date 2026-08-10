#!/usr/bin/env python3

import ast
import os

BANNER = r"""
    ____             __   _____ ___   __________
   / __ \____ ______/ /__/ ___//   | / ___/_  __/
  / / / / __ `/ ___/ // /\__ \/ /| | \__ \ / /
 / /_/ / /_/ / /  / ,<  ___/ / ___ |___/ // /
/_____/\__,_/_/  /_/|_|/____/_/  |_/____//_/

                DarkSAST v1.0
      Lightweight Python SAST
"""

class SecurityVisitor(ast.NodeVisitor):

    def __init__(self):
        self.findings = []

    def report(self, lineno, severity, message):
        self.findings.append(
            f"[{severity}] Line {lineno}: {message}"
        )

    def visit_Call(self, node):

        if isinstance(node.func, ast.Name):
            if node.func.id == "eval":
                self.report(
                    node.lineno,
                    "HIGH",
                    "eval() usage"
                )

            elif node.func.id == "exec":
                self.report(
                    node.lineno,
                    "HIGH",
                    "exec() usage"
                )

        elif isinstance(node.func, ast.Attribute):

            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
                and node.func.attr == "system"
            ):
                self.report(
                    node.lineno,
                    "HIGH",
                    "os.system() usage"
                )

            elif (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pickle"
                and node.func.attr == "loads"
            ):
                self.report(
                    node.lineno,
                    "HIGH",
                    "pickle.loads() deserialization"
                )

            elif (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"
                and node.func.attr in (
                    "call",
                    "run",
                    "Popen",
                    "check_output",
                    "check_call"
                )
            ):

                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        self.report(
                            node.lineno,
                            "HIGH",
                            f"subprocess.{node.func.attr}() with shell=True"
                        )

        self.generic_visit(node)

    def visit_Assign(self, node):

        for target in node.targets:

            if isinstance(target, ast.Name):

                variable = target.id.lower()

                if any(
                    keyword in variable
                    for keyword in [
                        "password",
                        "passwd",
                        "pwd",
                        "secret",
                        "apikey",
                        "api_key",
                        "token"
                    ]
                ):

                    if isinstance(node.value, ast.Constant):

                        if isinstance(
                            node.value.value,
                            str
                        ):

                            self.report(
                                node.lineno,
                                "MEDIUM",
                                f"Hardcoded credential in variable '{target.id}'"
                            )

        self.generic_visit(node)


def scan_file(filepath):

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            source = f.read()

        tree = ast.parse(source)

        visitor = SecurityVisitor()
        visitor.visit(tree)

        return visitor.findings

    except SyntaxError as e:

        return [
            f"[ERROR] Syntax error at line {e.lineno}: {e.msg}"
        ]

    except Exception as e:

        return [
            f"[ERROR] {e}"
        ]


def scan_directory(path):

    total_files = 0
    total_findings = 0

    for root, dirs, files in os.walk(path):

        for file in files:

            if file.endswith(".py"):

                total_files += 1

                filepath = os.path.join(root, file)

                findings = scan_file(filepath)

                if findings:

                    total_findings += len(findings)

                    print("\n" + "=" * 80)
                    print(filepath)
                    print("=" * 80)

                    for finding in findings:
                        print(finding)

    print("\n" + "=" * 80)
    print("SCAN SUMMARY")
    print("=" * 80)
    print(f"Files Scanned : {total_files}")
    print(f"Findings      : {total_findings}")


def main():

    print(BANNER)

    target = input(
        "Target directory (default: current directory): "
    ).strip()

    if not target:
        target = "."

    scan_directory(target)


if __name__ == "__main__":
    main()
