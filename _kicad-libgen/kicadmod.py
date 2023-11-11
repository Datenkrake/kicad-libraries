


def update_kicadmod_model(filename):
    # Read the file and store its content in a list
    with open(f'JLC2KiCad_lib/footprint/{filename}', 'r') as f:
        lines = f.readlines()

    # for each line in the file
    for i, line in enumerate(lines):
        if '(model JLC2KiCad_lib/footprint/packages3d/' in line:
            lines[i] = lines[i].replace('JLC2KiCad_lib/footprint/packages3d/', '')
        
    # Write the modified lines to a new file
    with open(f'JLC2KiCad_lib/footprint/{filename}', 'w') as f:
        f.writelines(lines)
    
    return