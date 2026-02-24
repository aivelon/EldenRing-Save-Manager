# convert bytes to human readable format
from hexedit import get_all_inventory, get_slot_ls, l_endian, search_itemid


def read_bytes(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def decode_bytes(data, encoding="utf-8", errors="replace"):
    return data.decode(encoding, errors=errors)


def convert_bytes(file_path, encoding="utf-8", errors="replace"):
    data = read_bytes(file_path)
    return decode_bytes(data, encoding=encoding, errors=errors)


def preview_hex(data, length=64):
    return data[:length].hex()


def find_item_by_three_files(f1, f2, f3, q1, q2, q3, slot=6):
    """
    Find item ID by comparing three save files with different quantities.

    Args:
        f1, f2, f3 (str): Paths to three save files
        q1, q2, q3 (int): Quantities in each respective file
        slot (int): Character slot to search (default: 6)

    Returns:
        list: ["match", [id1, id2]] for single match,
              ["multi-match", {index: [id1, id2], ...}] for multiple matches,
              None if no matches found
    """
    # Get slot data from each file using get_slot_ls
    # c1 = get_slot_ls(f1)[slot - 1]
    # c2 = get_slot_ls(f2)[slot - 1]
    # c3 = get_slot_ls(f3)[slot - 1]
    with open(f1, 'rb') as f, open(f2, 'rb') as ff, open(f3, 'rb') as fff:
        dat = f.read()
        dat2 = ff.read()
        dat3 = fff.read()
        c1 = get_slot_ls(f1)[slot - 1]
        c2 = get_slot_ls(f2)[slot - 1]
        c3 = get_slot_ls(f3)[slot - 1]
        dict_1 = get_item_id_by_quantity(c1, q1)
        dict_2 = get_item_id_by_quantity(c2, q2)
        dict_3 = get_item_id_by_quantity(c3, q3)
        d_1 = {k: v for k, v in dict_1.items()}
        d_2 = {k: v for k, v in dict_2.items()}
        d_3 = {k: v for k, v in dict_3.items()}
        # find common item ids with same type across all three files. d_1 is a dict of index to list of [id1, id2, type1, type2]
        # list items cannot be used in sets
        common_ids = set(tuple(v) for v in d_1.values()) & set(tuple(v) for v in d_2.values()) & set(tuple(v) for v in d_3.values())

        if not common_ids:
            return None
        elif len(common_ids) == 1:
            return ["match", list(common_ids)[0]]
        else:
            multi_match = {}
            for k, v in dict_1.items():
                if tuple(v) in common_ids:
                    multi_match[k] = v
                    print(f"Match found at index {k} with item ID {v[0:2]} and type {v[2:4]}")

            # keep item ids that only occur once across all the common ids to narrow down to most likely match
            id_counts = {}
            for item in common_ids:
                id_tuple = tuple(item[0:2])  # item ID is the first two elements of the list
                id_counts[id_tuple] = id_counts.get(id_tuple, 0) + 1

            most_likely_ids = {id_tuple for id_tuple, count in id_counts.items() if count == 1}
            # print(f"Most likely item IDs based on unique occurrences: {most_likely_ids}")
            # print their types also
            for item in common_ids:
                id_tuple = tuple(item[0:2])
                if id_tuple in most_likely_ids:
                    print(f"Most likely match with unique item ID {id_tuple} and type {item[2:4]}")
    return ["multi-match", multi_match]


def get_item_id_by_quantity(c1, q1):
    index = []

    for ind, i in enumerate(c1):
        # Check if quantities match across all three files
        if (l_endian(c1[ind:ind + 1]) == int(q1)): # and l_endian(c2[ind:ind + 1]) == int(q2) and l_endian(c3[ind:ind + 1]) == int(q3)):

            index.append(ind)
            # Verify UID pattern
            # if ((l_endian(c1[ind - 2:ind - 1]) == 0 and l_endian(c1[ind - 1:ind]) == 176) or
            #         (l_endian(c1[ind - 2:ind - 1]) == 128 and l_endian(c1[ind - 1:ind]) == 128)):
            #     index.append(ind)

    dict_1 = {}
    for i in index:
        dict_1[i - 6] = [l_endian(c1[i - 4:i - 3]), l_endian(c1[i - 3:i - 2]), l_endian(c1[i - 2:i - 1]), l_endian(c1[i - 1:i])]
    return dict_1

if __name__ == "__main__":
    file_1 = "./data/save-files/fragments_7/ER0000.sl2"
    file_2 = "./data/save-files/fragments_9/ER0000.sl2"
    file_3 = "./data/save-files/fragments_11/ER0000.sl2"
    print(find_item_by_three_files(file_1, file_2, file_3, 7, 9, 11))
