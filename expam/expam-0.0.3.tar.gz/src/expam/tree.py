import json
import os


def simulate_balanced_phylogeny(names):
    """
    :param names: List - list of leaf names.
    """

    # Declare an index.
    index = Index()

    # Insert all children.
    for name in names:
        # Make child node.
        childNode = Location(
            name=name,
            type="Leaf",
            dist=1.0
        )
        # Insert into tree.
        index.append(childNode)

    # Naming string.
    _NAME = len(names) - 1

    # Repeatedly join pairs until a full tree is made.
    while len(names) > 1:
        new_names = []

        while len(names) > 0:
            try:
                # Get next two children.
                child_names = []
                i = 0
                while i < 2:
                    child_names.append(names.pop())
                    i += 1

            except IndexError:
                # Only one child left. Just pass on the name.
                new_names.append(child_names[0])
                break

            # Join these children:
            # Make a parent node.
            parentName = str(_NAME)
            _NAME -= 1
            # Make a new Location.
            parentNode = Location(
                name=parentName,
                type="Branch"
            )
            print(f'New Parent {parentName}...')
            # Apply join.
            index.join(
                child_names[0],
                child_names[1],
                parentNode
            )

            # Append parent name to new_names.
            new_names.append(parentName)

        # New lot of children.
        names = new_names

    # Convert tree to newick format.
    return index.to_newick() + ";"


def propose_lca(c1, c2):
    """
    Given two binary coordinates, compute the shortest common prefix.

    :param coord: Indexable.
    :return: List.
    """
    m = min(len(c1), len(c2))
    if m == 0:
        return []

    for i in range(1, m+1):
        if c1[-i] != c2[-i]:
            if i == 1:
                return []
            else:
                return c1[-i+1:]
    else:
        return c1[-m:]


class Location:
    is_root = False

    def __init__(self, name="", type="", dist=0.0, coord=None, mag=0, accession_id=None, taxid=None, **kwargs):
        self._name = name
        self._type = type
        self._distance = dist
        self._coordinate = [] if coord is None else coord
        self._nchildren = 0
        self._magnitude = mag
        self._accession_id = accession_id
        self._taxid = taxid

        self.children = []
        self.primaryChild = None

    def __str__(self):
        return (f"Location - {self._name} ({self._type}):"
                f"\n\t+ Coordinate: {self._coordinate}"
                f"\n\t+ Children: {self._nchildren}")

    def name():
        doc = "The name property."

        def fget(self):
            return self._name

        def fset(self, value):
            self._name = value

        def fdel(self):
            del self._name

        return locals()

    name = property(**name())

    def type():
        doc = "The type property."

        def fget(self):
            return self._type

        def fset(self, value):
            self._type = value

        def fdel(self):
            del self._type

        return locals()

    type = property(**type())

    def distance():
        doc = "The distance property."

        def fget(self):
            return self._distance

        def fset(self, value):
            self._distance = value

        def fdel(self):
            del self._distance

        return locals()

    distance = property(**distance())

    def coordinate():
        doc = "The coordinate property."

        def fget(self):
            return self._coordinate

        def fset(self, value):
            self._coordinate = value

        def fdel(self):
            del self._coordinate

        return locals()

    coordinate = property(**coordinate())

    def nchildren():
        doc = "The nchildren property."

        def fget(self):
            return self._nchildren

        def fset(self, value):
            self._nchildren = value

        def fdel(self):
            del self._nchildren

        return locals()

    nchildren = property(**nchildren())

    def magnitude():
        doc = "The magnitude property."

        def fget(self):
            return self._magnitude

        def fset(self, value):
            self._magnitude = value

        def fdel(self):
            del self._magnitude

        return locals()

    magnitude = property(**magnitude())

    def accession_id():
        doc = "The accession id property."

        def fget(self):
            return self._accession_id

        def fset(self, value):
            self._accession_id = value

        def fdel(self):
            del self._accession_id

        return locals()

    accession_id = property(**accession_id())

    def taxid():
        doc = "The accession id property."

        def fget(self):
            return self._taxid

        def fset(self, value):
            self._taxid = value

        def fdel(self):
            del self._taxid

        return locals()

    taxid = property(**taxid())

    @classmethod
    def make_branch(cls, branch_name):
        return Location(branch_name, "Branch", 0)

    @classmethod
    def make_leaf(cls, tree, leaf_name, dist):
        return Location(leaf_name, "Leaf", dist)

    def add_child(self, child, primary_child=False):
        self.children.__setitem__(child.name, child)
        # Set as primary.
        if primary_child:
            self.set_primary(child)

    def set_primary(self, node):
        self.primaryChild = node

    def save(self, out_dir):
        fname = f'{self._name}.loc'
        with open(os.path.join(out_dir, "phylogeny", "loc", fname), 'w') as f:
            json.dump(self.__dict__, f)


class Index:
    def __init__(self):
        self._pointers = {}
        self.pool = [Location()]

    def __len__(self):
        return len(self.pool)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<Phylogeny Index, length={len(self)}>'

    @classmethod
    def load_newick(cls, url):
        newick_str = ""

        if not os.path.exists(url):
            raise OSError("Couldn't find path %s." % url)

        with open(url, "r") as f:
            for line in f:
                newick_str += line.strip()

        return cls.from_newick(newick_str)

    @classmethod
    def from_newick(cls, newick_string):
        """
        Parse Newick string...

        :param newick_string: String - Newick format phylogeny.
        :return: Index.
        """

        # Remove whitespace.
        newick_string = newick_string.replace(" ", "")

        print("* Initialising node pool...")
        index_pool = cls.init_pool(newick_string)

        print("* Checking for polytomies...")
        cls.resolve_polytomies(index_pool)

        print("* Finalising index...")
        leaf_names, index = cls.from_pool(index_pool)

        return leaf_names, index

    @staticmethod
    def init_pool(newick):
        """
        Given some phylogeny in Newick format, return a pool list
        to be used in the corresponding expam Index.

        :param newick: String - Newick format phylogeny.
        :return: List.
        """
        pool = [Location()]

        i = 0
        parent_stack = []
        currentNode = None

        #
        # Create a new node.
        #
        def new_node(name, type):
            nonlocal currentNode

            currentNode = Location(name, type)

            pool.append(currentNode)

            # Top node has no ancestor.
            if len(parent_stack) > 0:
                parent_stack[-1].children.append(currentNode)

        #
        # Get node name.
        #
        def close_branch():
            nonlocal parent_stack, currentNode, i, newick, NEWICK_PARSE

            current_branch = parent_stack.pop()

            # Get this branch's name, if it is given.
            if newick[i+1] not in NEWICK_PARSE:
                i += 1
                branch_name = parse_string()

                current_branch.name = branch_name

            currentNode = current_branch

        #
        # New branch in phylogeny and parent stack.
        #
        def new_branch():
            nonlocal currentNode

            new_node(name="", type="Branch")
            parent_stack.append(currentNode)

        #
        # New Leaf in phylogeny.
        #
        def new_leaf():
            nonlocal currentNode

            new_node(name="", type="Leaf")

        #
        # Parse name.
        #
        def parse_string(force_digits=False):
            nonlocal i  # Inherit current index.

            j = i + 1

            while newick[j] not in NEWICK_PARSE:
                j += 1
            string = newick[i:j]

            # Check formatting.
            if force_digits:
                try:
                    string = float(string)

                except ValueError:
                    raise ValueError("Invalid distance declaration %s!" % newick[i:j])

            i = j - 1  # Update current index position.

            return string

        #
        # Clear current node (stack-ish).
        #
        def clear_node():
            nonlocal currentNode

            currentNode = None

        #
        # Set distance of current node.
        #
        def set_node_distance():
            nonlocal currentNode, i

            i += 1  # Skip ':' character.
            currentNode.distance = parse_string(force_digits=True)

        #
        # Do nothing.
        #
        def finisher():
            nonlocal i

            i = len(newick)

        # Parsing functions for Newick format.
        NEWICK_PARSE = {
            "(": new_branch,
            ")": close_branch,
            ",": clear_node,
            ":": set_node_distance,
            ";": finisher
        }

        # Parsing loop.
        while i < len(newick):
            if newick[i] in NEWICK_PARSE:
                NEWICK_PARSE[newick[i]]()

            else:
                new_leaf()

                currentNode.name = parse_string()

            i += 1

        # Return pool array for insertion into expam Index.
        return pool

    @staticmethod
    def resolve_polytomies(pool):
        """
        If the phylogeny contains polytomies, continually join the first two
        children with parents of distance 0 until the polytomy is resolved.

        :param pool: List.
        :return: None - inplace.
        """
        # Processing loop.
        i = 1
        while i < len(pool):
            node = pool[i]

            # Continually join first two nodes.
            while len(node.children) > 2:
                print("\tPolytomy (degree=%d) detected! Resolving..."
                      % len(node.children))

                # Declare new parent of distance 0.
                newParent = Location(
                    name="",
                    type="Branch",
                    dist=0.0
                )

                # Replace children.
                for _ in range(2):
                    newParent.children.append(node.children.pop(0))

                # Insert into pool.
                node.children.append(newParent)
                pool.insert(i + 1, newParent)

            i += 1

    @classmethod
    def from_pool(cls, pool):
        """
        Import some previously created, Newick format, pool of nodes.
        To import pool:
            - Update name map.
            - Set branch names.
            - Set coordinates.

        :param pool: List.
        :return: List (leaf names), Index.
        """
        leaf_names = []

        # Initialise expam Index.
        index = cls()
        index.pool = pool

        branch_id = 1
        for i, node in enumerate(pool):
            if i == 0:
                continue

            if node.type == "Branch":
                # Set branch name.
                node.name = str(branch_id)
                branch_id += 1

            else:
                # Store leaf names.
                leaf_names.append(node.name)

            # Set name mapping.
            index._pointers[node.name] = i

        # Replace children objects with respective names.
        # Note: This requires the name mapping to be complete...
        for node in pool[1:]:
            if node.type == "Branch":
                i = 0
                while i < len(node.children):
                    node.children[i] = node.children[i].name

                    i += 1

        # Set (binary) coordinates.
        index.update_coordinates()

        # Update nchildren.
        index.update_nchildren()

        return leaf_names, index

    def append(self, item):
        """
        Mostly used for initialisation stage: insert an item in to the pool
            and declare its pointer.

        :param item: String - coordinate.
        """
        # Declare an index.
        index = len(self.pool)

        # Set pointer.
        self._pointers[item.name] = index

        self.pool.append(item)

    def join(self, a, b, glue, dist=None):
        """
        Join indices a & b - in place.

        :param a, b: String - Names of items (indices).
        :param glue: Location - parent of a & b.
        """
        if dist is None:
            dist = [1.0, 1.0]
        i, j = self._pointers[a], self._pointers[b]
        i, j = self.smaller(i, j)  # i < j.

        one, two = j, self.neighbouring(j)
        three = self.neighbouring(i)
        self.move([one, two], three)

        self.insert(i, glue)

        # Update number of children and distances.
        glue.children.extend((a, b))

        for i, child in enumerate([a, b]):
            glue.nchildren += 1 + ((self[child].type == "Branch") * self[child].nchildren)

            self[child].distance = dist[i]

    def move(self, i, j):
        """
        Move items in pool @ i to j.
            NOTE: i > j.

        :param i: List - indices from range [inclusive, exclusive] to be moved.
        :param j: Int - Index to move items.
        """
        width = i[1] - i[0]

        if i[0] == j:
            return

        # Delete affected pointers.
        for n in range(j, i[1]):
            del self._pointers[n]

        # Retrieve items to be moved.
        temp = []
        for n in range(width):
            temp.append(self.pool.pop(i[1] - (n + 1)))

        # Insert these items in at j. Since they were popped in reverse order,
        # insert append them in the same index to revert back to the original
        # order.
        for obj in temp:
            self.pool.insert(j, obj)

        # Update pointers.
        for n in range(j, i[1]):
            self._pointers[n] = self.pool[n].name

    def insert(self, i, item):
        """
        Insert item into Pool at index i. This will update bumped items.
        """
        # Update pointers.
        for n in range(i, len(self.pool)):
            loc = self.pool[n]

            self._pointers[loc.name] = n + 1

        self.pool.insert(i, item)
        self._pointers[item.name] = i

    def __setitem__(self, key, value):
        self.pool[self._pointers[str(key)]] = value

    def __getitem__(self, key):
        return self.pool[self._pointers[str(key)]]

    def __delitem__(self, key):
        self.pool.pop(self._pointers[key])

    def neighbouring(self, i):
        return i + 1 + self.pool[i].nchildren

    def update_coordinates(self):
        """
        Update coordinates after a join.

        - Depth of 0 corresponds to top level.
        - Child counting starts at 0 as first child.

        :param i: Int - index of new branch i.e. all changes to the right.
        """
        coord, i = [-1], 1

        while i < len(self.pool):
            while coord[0] + 1 > 1:
                coord.pop(0)

            coord[0] += 1

            if self.pool[i].type == "Branch":
                self.pool[i].coordinate = list(coord[:-1])

                coord.insert(0, -1)
            else:  # It's a leaf.
                self.pool[i].coordinate = list(coord[:-1])

            i += 1

    def update_nchildren(self):
        """
        By updating from right of pool to left, we are guaranteed
        to encounter all children before their parent, so we can
        simply loop without recursion.

        :return:
        """
        for j in range(len(self.pool) - 1, 0, -1):
            node = self.pool[j]

            node.nchildren = len(node.children) + sum([
                self[child].nchildren
                for child in node.children
            ])

    def coord(self, coordinate):
        """
        Return Location at `coordinate`.

        :param coordinate:
        :return: Location
        """
        pool_index = 1

        for step in coordinate[::-1]:
            pool_index += 1
            pool_index += int(step) * (self.pool[pool_index].nchildren + 1)

        return self.pool[pool_index]

    def print_index(self):
        for l in self.pool:
            print(l.name, l.coordinate, l.nchildren)

    @staticmethod
    def smaller(a, b):
        if a < b:
            return a, b
        return b, a

    def to_newick(self):
        NODE_FORMAT = "$node$"

        newick = "(%s,%s)%s;" % (NODE_FORMAT, NODE_FORMAT, self.pool[1].name)
        node_formats = {
            "Branch": "(%s,%s){name}:{distance}" % (NODE_FORMAT, NODE_FORMAT),
            "Leaf": "{name}:{distance}"
        }

        for node in self.pool[2:]:

            node_data = node_formats[node.type].format(name=node.name, distance=node.distance)
            newick = newick.replace(NODE_FORMAT, node_data, 1)

        return newick
