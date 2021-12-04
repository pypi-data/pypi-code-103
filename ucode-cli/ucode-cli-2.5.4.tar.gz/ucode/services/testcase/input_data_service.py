from dataclasses import dataclass, field
from typing import List, Union, Optional

from dataclasses_json import dataclass_json
from ucode.helpers.clog import CLog
from ucode.services.common import find_section


def try_cast(v, _type):
    try:
        v = _type(v)
    except ValueError:
        pass
    except TypeError:
        pass

    return v


@dataclass_json
@dataclass
class InputVariable:
    name: str = ""
    data_type: str = "" # integer, float, string, array.integer, array.array.float...
    min_value: str = None # Number or variable name
    max_value: str = None # Number or variable name
    available_values: str = None # set of value {...} or string ""
    min_value_inclusive: bool = True
    max_value_inclusive: bool = True

    # Number or variable name for 1D-array
    # list of 2 value (Number or variable name): min_len & max_len for string, always inclusive those two boundaries
    # list of number or variable name for multidimension arrays, each for 1 dimension
    # None for others
    length: Union[Union[int, str], List[Union[int, str]]] = None
    item_var: '__class__' = None    # input variable cua item (for string, array, multidimension array)

    def parse(self, _raw: str):
        _type, _name = _raw.split()
        # print(_type, " - ", _name)
        if _type in ['float', 'double', 'long double']:
            self.data_type = 'float'
            self.name = _name
        elif _type in ['int', 'integer']:
            self.data_type = 'integer'
            self.name = _name
        elif _type in ['str', 'string']:
            self.data_type = 'string'
            self.name = _name
        elif _type.startswith('array'):
            self.data_type = _type
            i = _name.find("[")
            self.name = _name[:i]
            sizes = _name[i:].replace("[", " ").replace("]", " ").split()
            for j in range(len(sizes)):
                if sizes[j].isdigit():
                    sizes[j] = int(sizes[j])
                else:
                    sizes[j] = f"`{sizes[j]}`"
            if len(sizes) == 1:
                self.length = sizes[0]
            else:
                self.length = sizes
        else:
            CLog.error("Not supported data type `%s` for variable `%s`" % (_type, _name))

    def parse_constraint(self, var_raw: str, L, H, is_min_inclusive, is_max_inclusive, available_values):
        """

        @param var_raw: a | s.length | a[i] | s[i] | a[i][j]
        @param L:
        @param H:
        @param is_min_inclusive:
        @param is_max_inclusive:
        @param available_values:
        @return:
        """
        if var_raw == self.name:
            self.min_value = L
            self.max_value = H
            self.min_value_inclusive = is_min_inclusive
            self.max_value_inclusive = is_max_inclusive
            self.available_values = available_values
        elif var_raw == self.name + ".length": # for string
            self.length = (L, H)
        elif var_raw.index("[") > 0:
            self.item_var = InputVariable()
            if var_raw.endswith(".length"):
                self.item_var.length = (L, H)
            else:
                self.item_var.min_value = L
                self.item_var.max_value = H
                self.item_var.min_value_inclusive = is_min_inclusive
                self.item_var.max_value_inclusive = is_max_inclusive
                self.item_var.available_values = available_values
        else:
            CLog.error("Constraint not supported: " + var_raw)

@dataclass_json
@dataclass
class InputLine:
    index: int = 0
    raw: str = ""
    description: str = ""
    repeat: Union[int, str] = 1  # number or variable name
    variables: List[InputVariable] = field(default_factory=list)

    def parse(self, _raw: str):
        self.raw = _raw
        raw_vars = _raw.lstrip("- ")
        dash_i = raw_vars.find("-")
        if dash_i >= 0:
            self.description = raw_vars[dash_i+1:].strip()
            raw_vars = raw_vars[:dash_i]
        raw_vars = raw_vars.strip()

        L = 0
        while L < len(raw_vars):
            R = L
            if raw_vars[L] == '`':
                R = L+1
                while R < len(raw_vars) and raw_vars[R] != '`':
                    R += 1
                var = raw_vars[L+1:R]
                if var.startswith("["):
                    self.repeat = var.lstrip("[").rstrip("]")
                    print("repeat: ", self.repeat)
                else:
                    input_var = InputVariable()
                    input_var.parse(var)
                    self.variables.append(input_var)
            L = R+1
        # print(raw_vars)


@dataclass_json
@dataclass
class InputSpecification:
    output_spec: str = ""
    multiple_testcase: bool = False
    multiple_testcase_var: InputVariable = None
    input_lines: List[InputLine] = field(default_factory=list)

    def find_var_by_name(self, name: str) -> Optional[InputVariable]:
        if self.multiple_testcase_var and self.multiple_testcase_var.name == name:
            return self.multiple_testcase_var
        for input_line in self.input_lines:
            for v in input_line.variables:
                if v.name == name:
                    return v
        return None

    def parse_constraint(self, constraint: str):
        var, limit = constraint.lstrip().lstrip("-").strip().split(":")
        var = var.strip("`")
        # print(var, limit)
        i = 0
        while i<len(var) and var[i] != "." and var[i] != "[":
            i += 1
        var_name = var[:i]
        # print("name:", var_name)

        limit: str = limit.strip()
        is_min_inclusive = limit.startswith("[")
        is_max_inclusive = limit.endswith("]")
        available_values = None
        L = H = None
        if limit.startswith("[") or limit.startswith("("):
            L, H = [v.strip() for v in limit.strip("[]()").split(",")]
        elif limit.startswith("{") and limit.endswith("}"):
            available_values = eval(limit)
        else:
            available_values = limit.lstrip("'").rstrip("'").lstrip('"').rstrip('"')
        # print(L, H, is_min_inclusive, is_max_inclusive, available_values)

        if var_name == "Subtasks":
            return

        input_var = self.find_var_by_name(var_name)
        print(f"found input var name `{var_name}`:", input_var)
        if not input_var:
            CLog.error(f"Variable not defined in input, but found in constraints: ``{var_name}")
            return

        # support integer and array.integer and s.length
        if "integer" in input_var.data_type or "float" in input_var.data_type or "length" in var:
            L = try_cast(L, float)  # call this first for integer value, to support "1e9"
            H = try_cast(H, float)
            if "integer" in input_var.data_type or "length" in var:
                L = try_cast(L, int)
                H = try_cast(H, int)

        input_var.parse_constraint(var, L, H, is_min_inclusive, is_max_inclusive, available_values)

    def parse(self, input_desc: str, constraints: str, output_desc: str):
        # input parsing
        lines = input_desc.strip().splitlines()
        if not lines:
            CLog.error("Empty input")
            return None
        if not (lines[0].startswith("[//]: # ") and "Auto" in lines[0]):
            CLog.error("This works for auto generate input format only. "
                       "Input description should start with line: [//]: # (Auto)")
            return None

        indices, content = find_section("^-", lines, start_index=1, until_pattern="^-", skip_section_header=False)
        # print(*lines, sep="\n")

        i = 0
        for idx in indices:
            i += 1
            input_line = InputLine(index=i)
            raw_lines = " ".join([s.strip() for s in content[idx]])
            input_line.parse(raw_lines)
            if input_line.description.startswith("Multitest"):
                self.multiple_testcase = True
                self.multiple_testcase_var = input_line.variables[0]
            else:
                self.input_lines.append(input_line)
            # print(input_line)

        # constraints parsing
        lines = constraints.strip().splitlines()
        if not lines:
            CLog.error("Empty constraints")
            return None

        indices, content = find_section("^-", lines, start_index=0, until_pattern="^-", skip_section_header=False)
        print(indices, content, sep="\n")
        for idx in indices:
            self.parse_constraint(content[idx][0])

        # output parsing
        self.output_spec = output_desc
        return self


def test_generate_data():
    _input_desc = """
[//]: # (Auto)
- `integer T` - Multitest
- `integer n` `integer m` - Số lượng phần tử $n$, 
số lượng thao tác $m$
- `int x` - số nguyên trong tập {2, 3, 5, 8} 
- `string name` - Tên
- `array.string subject[3][x]` - Tên
- `array.integer a[n]` - Các phần tử $a_i$ của mảng $a$, 
cách nhau bởi dấu cách
- `array.array.float b[n][m]` - Ví dụ ma trận 
- `double L` `double R` `[m]` - Cận trái và phải của một 
trong số $m$ thao tác 
"""

    _output_desc = """
- output is freedom for now
- `boolean YES|NO` - Kết quả bài toán
- `integer`- Kết quả bài toán
- `float(3)`- Kết quả bài toán, với 3 chữ số sau dấu phẩy
"""

    _constraints = """
- `T`: [1, 100]
- `n`: (2, 1e6]
- `m`: (2, 1e4)
- `x`: {2, 3, 5, 8}
- `a[i]`: [1, 1e18)
- `name.length`: [8, 8]
- `name[i]`: "qwertyuiopasdfghjklzxcvbnm"
- `subject[i].length`: [10, 20]
- `b[i][j]`: (1.1, 2.1)
- `L`: (1, 10000) 
- `R`: (`L`, 10000)
- Subtasks:
    - 40%: 
        - `T`: [1, 10]
        - `n`: [1, 100]
    - 30%: 
        - `n`: [100, 10000]
    - 40%: 
        - `n`: [10000, 1e6]
"""

    input_spec = InputSpecification()
    input_spec.parse(_input_desc, _constraints, _output_desc)

    print("Spec: ")
    print(input_spec.to_json())


if __name__ == "__main__":
    # folder = "D:\\projects\\ucode\\_problem_dev\\big_mod_py"
    # T = TestcaseService.generate_testcases(problem_folder=folder, format="ucode", testcase_count=20)
    # print("testcases:", len(T))

    test_generate_data()

