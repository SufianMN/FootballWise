import os

app_dir = r"C:\Users\sufia\OneDrive\Desktop\FootballWise\server\app"

def refactor_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    if 'print(' not in content and 'print_exc()' not in content:
        return
        
    lines = content.split('\n')
    
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
            
    if 'from app.core.logger import get_logger' not in content:
        lines.insert(insert_idx, 'from app.core.logger import get_logger')
        lines.insert(insert_idx + 1, 'logger = get_logger(__name__)')
        
    for i in range(len(lines)):
        if 'print(' in lines[i] and not 'logger' in lines[i]:
            if 'Error' in lines[i] or 'missing!' in lines[i]:
                lines[i] = lines[i].replace('print(', 'logger.error(')
            elif 'Warning' in lines[i]:
                lines[i] = lines[i].replace('print(', 'logger.warning(')
            else:
                lines[i] = lines[i].replace('print(', 'logger.info(')
        if 'traceback.print_exc()' in lines[i]:
             lines[i] = lines[i].replace('traceback.print_exc()', 'logger.error("Exception occurred", exc_info=True)')
             
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

for root, dirs, files in os.walk(app_dir):
    for file in files:
        if file.endswith('.py'):
            refactor_file(os.path.join(root, file))
