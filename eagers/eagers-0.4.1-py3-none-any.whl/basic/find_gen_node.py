"""Functionality for finding out which node a generator is at.
"""


def find_gen_node(gen, subnet):
    """Find out which node the given generator exists at."""
    gen_in_network = {}
    for k, v in subnet.items():
        if k == "network_names":
            continue
        for i, node in enumerate(v["equipment"]):
            if gen["name"] in node:
                gen_in_network[k] = i
                break
        else:
            # break was not reached.
            gen_in_network[k] = None
    gen_network = None
    i_node = None
    for network_type in subnet["network_names"]:
        if gen_in_network[network_type] is not None:
            gen_network = network_type
            i_node = gen_in_network[network_type]
            break
    if not gen_network:
        raise RuntimeError(f"No network found for generator {gen['name']!r}")
    return gen_network, i_node
