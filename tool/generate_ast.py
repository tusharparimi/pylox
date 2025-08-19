import sys
from typing import TextIO

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_ast.py [output_dir]", file=sys.stderr)
        sys.exit(64)
    output_dir: str = sys.argv[1]
    define_ast(output_dir, "Expr", [
        "Binary     = left: Expr, operator: Token, right: Expr",
        "Grouping   = expression: Expr",
        "Literal    = value: object",
        "Unary      = operator: Token, right: Expr"
    ])

def define_ast(output_dir: str, base_name: str, types: list[str]) -> None:
    try:
        path: str = output_dir + "/" + base_name.lower() + ".py"
        with open(path, mode="w", encoding="utf-8") as file:
            file.write("from abc import ABC")
            file.write("\n")
            file.write("from dataclasses import dataclass")
            file.write("\n")
            file.write("from tokens import Token")
            file.write("\n\n")
            file.write(f"class {base_name}(ABC):")
            file.write("\n\tpass")

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

if __name__ == "__main__":
    main()
