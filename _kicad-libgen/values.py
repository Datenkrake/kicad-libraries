



def find_values(jlcparts_data: dict):

    description = jlcparts_data["Description"]
    if description is None:
        return None
    # split the description by ' '
    description = description.split(" ")
    # find list items that contain capital V
    ohm = chr(937)
    R = [item for item in description if ohm in item]
    # remove items where ohm is not the last character
    R = [item for item in R if item[-1] == ohm]
    F = [item for item in description if "F" in item]
    F = [item for item in F if item[-1] == "F"]
    H = [item for item in description if "H" in item]
    H = [item for item in H if item[-1] == "H"]

    V = [item for item in description if "V" in item]
    V = [item for item in V if item[-1] == "V"]
    W = [item for item in description if "W" in item]
    W = [item for item in W if item[-1] == "W"]

    percent = [item for item in description if "%" in item]
    percent = [item for item in percent if item[-1] == "%"]
    ppm = [item for item in description if "ppm" in item]
    ppm = [item for item in ppm if item[-3:] == "ppm"]

    KB = [item for item in description if "KB" in item]
    KB = [item for item in KB if item[-2:] == "KB"]
    MHz = [item for item in description if "MHz" in item]
    MHz = [item for item in MHz if item[-3:] == "MHz"]
    A = [item for item in description if "A" in item]
    A = [item for item in A if item[-1] == "A"]

    # create a list of values from the above lists in the following order:
    # R, F, H, V, W, percent, ppm, KB, MHz, A
    values = [R, F, H, V, W, percent, ppm, KB, MHz, A]
    # remove empty lists from the list of values
    values = [value for value in values if value != []]
    # remove items that do not contain at least one digit
    values = [value for value in values if any(char.isdigit() for char in value[0])]

    # create a dict with the keys value, value1, value2, value3, value4
    valuedict = {
        "value1": None,
        "value2": None,
        "value3": None,
        "value4": None
    }

    # assign first 4 values to value1, value2, value3, value4
    for i, value in enumerate(values):
        if value[0] is not None:
            valuedict[f"value{i+1}"] = value[0]
        if i == 3:
            break

    return valuedict