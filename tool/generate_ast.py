import sys
from typing import TextIO

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_ast.py [output_dir]", file=sys.stderr)
        sys.exit(64)
    output_dir: str = sys.argv[1]
    define_ast(output_dir, "Expr", [
        "Assign     = name: Token, value: Expr",
        "Binary     = left: Optional[Expr], operator: Token, right: Optional[Expr]",
        "Grouping   = expression: Expr",
        "Literal    = value: object",
        "Unary      = operator: Token, right: Expr",
        "Ternary    = condition: Expr, operator1: Token, expr_if_true: Expr, operator2: Token, expr_if_false: Expr",
        "Variable   = name: Token"
    ])

def main1():
    if len(sys.argv) != 2:
        print("Usage: generate_ast.py [output_dir]", file=sys.stderr)
        sys.exit(64)
    output_dir: str = sys.argv[1]
    define_ast(output_dir, "Stmt", [
        "Expression = expression: Expr",
        "Print      = expression: Expr",
        "Var        = name: Token, initializer: Optional[Expr]"
    ])

def define_ast(output_dir: str, base_name: str, types: list[str]) -> None:
    try:
        path: str = output_dir + "/" + base_name.lower() + ".py"
        with open(path, mode="w", encoding="utf-8") as file:
            file.write("from __future__ import annotations")
            file.write("\n")
            file.write("from abc import ABC, abstractmethod")
            file.write("\n")
            file.write("from dataclasses import dataclass")
            file.write("\n")
            file.write("from typing import Protocol, Optional")
            file.write("\n")
            file.write("from pylox.tokens import Token")
            file.write("\n\n")

            file.write("class Visitor(Protocol):")
            for type in types:
                type_name = type.split("=")[0].strip()
                # file.write("\n\t")
                # file.write("@staticmethod")
                file.write("\n\t")
                file.write(f"def visit_{type_name}_{base_name}(self, {type_name.lower()}: {type_name}): ...")

            file.write("\n\n")
            file.write(f"class {base_name}(ABC):")
            file.write("\n\t")
            file.write("@abstractmethod")
            file.write("\n\t")
            file.write("def accept(self, visitor: Visitor): ...")

            for type in types:
                class_name = type.split("=")[0].strip()
                fields = type.split("=")[1].strip()
                define_type(file, base_name, class_name, fields)

    except FileNotFoundError: print("File Path Invalid") 

def define_type(file: TextIO, base_name: str, class_name: str, fields: str) -> None:
    file.write("\n\n")
    file.write("@dataclass(frozen=True)")
    file.write("\n")
    file.write(f"class {class_name}({base_name}):")

    field_list = fields.split(", ")
    for field in field_list:
        file.write("\n\t")
        file.write(field)

    file.write("\n\n\t")
    file.write("def accept(self, visitor: Visitor):")
    file.write("\n\t\t")
    file.write(f"return visitor.visit_{class_name}_{base_name}(self)")

if __name__ == "__main__":
    main()
    main1()
