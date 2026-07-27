import ast
import sys
import os

stdlib = sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else set()
# Add some common ones just in case
stdlib.update(['os', 'sys', 'json', 'ast', 'time', 'logging', 'pathlib', 'traceback', 'typing'])

external_modules = set()

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in stdlib and not mod.startswith('.'):
                        external_modules.add(mod)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    mod = node.module.split('.')[0]
                    if mod not in stdlib:
                        external_modules.add(mod)
    except Exception as e:
        print(f"Failed to parse {filepath}: {e}")

for root, dirs, files in os.walk('server/app'):
    for file in files:
        if file.endswith('.py'):
            parse_file(os.path.join(root, file))
            
for root, dirs, files in os.walk('ml'):
    for file in files:
        if file.endswith('.py'):
            parse_file(os.path.join(root, file))

print("Found external modules:")
for mod in sorted(list(external_modules)):
    print(mod)
