



def clean_symbol(symbol):
    path = "JLC2KiCad_lib/symbol/"
    file = symbol+".kicad_sym"
    # open the file
    with open(f"{path}{file}", "r") as f:
        # read all lines
        lines = f.readlines()
    # find the first line that contains the string '(property "Reference"'
    for i, line in enumerate(lines):
        if '(property "Reference"' in line:
            delete_from = i+3
            break
    # find the last occurence of '(symbol' in the file
    for i, line in enumerate(reversed(lines)):
        if '(symbol' in line:
            delete_to = len(lines) - i - 1
            break
    # delete all lines between the first line that contains the string '(property "Reference"' and the last occurence of '(symbol'
    del lines[delete_from:delete_to]

    # write the modified lines to the file
    with open(f"{path}{file}", "w") as f:
        f.writelines(lines)

    return None