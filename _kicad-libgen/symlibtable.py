


def update_symlibtable(symbol: str):
    name = symbol
    type = "KiCad"
    file = name+".kicad_sym"
    visible = "hidden"
    uri = "${KICAD7_SYMBOL_DIR}/"+file
    # Specify the line you want to add
    new_line = f'  (lib (name "{name}")(type "{type}")(uri "{uri}")(options "")(descr "")({visible}))'

    # Read the existing file
    with open('sym-lib-table', 'r') as file:
        lines = file.readlines()

    # check if the line already exists
    for line in lines:
        if line.strip() == new_line.strip():
            return

    # Find the last enclosing bracket
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == ')':
            # Insert the new line before the last bracket
            lines.insert(i, new_line + '\n')
            break

    # Write the updated content back to the file
    with open('sym-lib-table', 'w') as file:
        file.writelines(lines)
    return
