def fix_orbit():
    import os
    path = 'c:/Users/magnu/OneDrive/Studie/Elsys/8. Semester/Navigation Systems/Code/NavSysLib/Orbit.py'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = []
    for line in text.split('\n'):
        if 'print(f"Iteration' in line or 'print(f"Transmission time' in line:
            continue
        lines.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

fix_orbit()
