from typing import List, Tuple, Dict, Optional
import libcst as cst

with open("test_airconditioner_miot.py") as f:
    code = f.read()


ast = cst.parse_module(code)

class TypingTransformer(cst.CSTTransformer):
    def __init__(self):
        # stack for storing the canonical name of the current function
        self.stack: List[Tuple[str, ...]] = []
        self.methods = []


    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        self.stack.append(node)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        self.stack.pop()
        return updated_node

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        name = original_node.name.value
        if not name.startswith("test_"):
            return updated_node.with_changes()

        print()
        #if 'TestCase' in [val.value.value for val in self.stack[0].bases]:
        #    print(f"Time to modify {original_node}")

        #self.stack.pop()
        # run updates here?
        return updated_node



transformer = TypingTransformer()
modified = ast.visit(transformer)
print(modified)