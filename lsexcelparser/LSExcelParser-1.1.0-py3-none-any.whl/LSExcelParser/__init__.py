import xlrd
import re
import copy

name = "LSExcelParser"


class HalBase:
    def __init__(self):
        self.used = 0


class HalDevice(HalBase):
    def __init__(self, d_class=None, *args, **kwargs):
        super(HalDevice, self).__init__()
        self._address_sub = re.compile(r"_")

        self.device_name = None
        self.memory_size = None
        self.device_address_base = None
        self.device_class_name = None
        for item in kwargs.items():
            if item[0] == "Name":
                self.device_name = kwargs["Name"]
            elif item[0] == "Size":
                self.memory_size = kwargs["Size"]
            elif item[0] == "Address":
                self.device_address_base = self._address_sub.sub("", kwargs["Address"])
            elif item[0] == "Class":
                self.device_class_name = kwargs["Class"]
        self.device_class = d_class

    def add_device_class(self, device_class):
        for reg in device_class:
            reg.base_address = self.device_address_base
        self.device_class = copy.deepcopy(device_class)

    def get_device_addr(self):
        return self.device_address_base

    def __iter__(self):
        return self.device_class

    def __call__(self, *args, **kwargs):
        return {
            "Name": self.device_name,
            "Address": self.device_address_base,
            "Size": self.memory_size,
        }


# This class is lucency for user
class HalDeviceClass(HalBase):
    def __init__(self, device):
        super(HalDeviceClass, self).__init__()
        self.device_class_name = device
        self._regiser = []
        self._count = 0

        self._temp_register = None
        self._find_indexs_pattern = re.compile(r"\[(?P<Number>[0-9]+)\]")
        self._locate_indexs_pattern = re.compile(r"<ARRAY_INDEX>")
        self._indexs_num = 0

    def add_regiser(self, reg):
        # There have a temporary register, need to expand
        if self._temp_register:
            self._expand()
            self._temp_register = None
        # If not find expand key word
        if not self._filter(reg):
            self._regiser.append(reg)

    def is_end(self):
        if self._temp_register:
            self._expand()
            self._temp_register = None

    def _filter(self, reg):
        rslt = self._find_indexs_pattern.search(reg.reg_name)
        if rslt:
            self._indexs_num = int(rslt.group("Number"))
            self._temp_register = reg
            return True
        else:
            return False

    def _expand(self):
        _register = None
        # Get register parameter
        para = self._temp_register()
        rslt = self._find_indexs_pattern.search(para["Name"])
        nickname = para["Name"][0: rslt.span()[0]]
        for num in range(self._indexs_num):
            _temp_para = copy.deepcopy(para)
            _temp_para["Name"] = nickname + str(num)
            _temp_para["Address"] = hex(int(para["Address"], 16) + num * 4)
            _register = Register(**_temp_para)
            for filed in self._temp_register.filed:
                # Get the new filed name
                filedname = self._locate_indexs_pattern.sub(str(num), filed.filed_name)
                # Filed it and add it in register
                f_para = filed()
                f_para["Name"] = filedname
                _register.add_filed(Filed(**f_para))

            self._regiser.append(_register)

    def __iter__(self):
        return self

    def __next__(self):
        if self._count >= len(self._regiser):
            self._count = 0
            raise StopIteration
        temp = self._regiser[self._count]
        self._count += 1
        return temp


class Register(HalBase):
    def __init__(self, *args, **kwargs):
        super(Register, self).__init__()
        self.reg_name = ""
        self.sub_addr = ""
        self.base_address = "0"
        self.reset_val = ""
        self.description = ""
        self.property = "NA"
        for item in kwargs.items():
            if item[0] == "Name":
                self.reg_name = kwargs["Name"]
            elif item[0] == "Address":
                try:
                    self.sub_addr = int(str("0x") + str(kwargs["Address"]), 16)
                except ValueError:
                    self.sub_addr = int(kwargs["Address"], 16)
            elif item[0] == "Value":
                self.reset_val = kwargs["Value"]
            elif item[0] == "Description":
                self.description = kwargs["Description"]
            elif item[0] == "Base_Address":
                self.base_address = kwargs["Base_Address"]
        self.filed = []
        self._count = 0

    def add_filed(self, filed):
        self.filed.append(filed)

    def __iter__(self):
        self._count = 0
        return self

    def __next__(self):
        if self._count >= len(self.filed):
            self._count = 0
            raise StopIteration
        temp = self.filed[self._count]
        self._count += 1
        return temp

    def __call__(self, *args, **kwargs):
        return {"Name": self.reg_name,
                "Address": hex(self.sub_addr + int(self.base_address, 16)),
                "Value": self.reset_val,
                "Description": self.description,
                "Property": self.property,
                }


class Filed(HalBase):
    def __init__(self, *args, **kwargs):
        super(Filed, self).__init__()
        self.filed_name = ""
        self.property = ""
        self.description = ""
        self.reset_val = ""
        self.start_bit = ""
        self.end_bit = ""
        for item in kwargs.items():
            if item[0] == "Name":
                self.filed_name = kwargs["Name"]
            elif item[0] == "Property":
                self.property = kwargs["Property"]
            elif item[0] == "Description":
                self.description = kwargs["Description"]
            elif item[0] == "Value":
                self.reset_val = kwargs["Value"]
            elif item[0] == "Start":
                self.start_bit = kwargs["Start"]
            elif item[0] == "End":
                self.end_bit = kwargs["End"]

        self._locate_indexs_pattern = re.compile(r"<ARRAY_INDEX>")

    def __call__(self, *args, **kwargs):
        return {"Name": self.filed_name,
                "Property": self.property,
                "Value": self.reset_val,
                "Start": self.start_bit,
                "End": self.end_bit,
                "Field": "%s : %s" % (self.start_bit, self.end_bit),
                "Description": self.description}


class PeripheralRegisterParser:
    def __init__(self, excel, dtc_dic, dev_dic="all", exclude=None):
        # Judge the excel path is exist
        if excel:
            self.excel_path = excel
            self._xlrd_handler = xlrd.open_workbook(self.excel_path)
        else:
            raise ValueError("Excel file path can't be None")

        if dtc_dic:
            self.dtc_dic = dtc_dic
        else:
            raise ValueError("Device to Class dictionary can't be empty")

        if dev_dic == "all":
            self.dev_dic = self._xlrd_handler.sheet_names()
        else:
            self.dev_dic = dev_dic

        # Strip the exclude sheet and (device to class) sheet
        if exclude:
            for i in exclude:
                try:
                    self.dev_dic.remove(i)
                except ValueError:
                    pass

        for i in self.dtc_dic:
            try:
                self.dev_dic.remove(i)
            except ValueError:
                pass

        self._device = []
        self._deviceclass = []

        self._dtc_dic_header = [{"Key": "Address Start"},
                                {"Key": "Module"},
                                {"Key": "Class"}]
        self._dtc_dic_reheader = ("Address", "Name", "Class")

        self._dev_dic_header = [{"Key": "Sub-Addr\n(Hex)", "Level": (1,), "Priority": ("H",)},
                                {"Key": "Start\nBit", "Level": (2,), "Priority": ("M",)},
                                {"Key": "End\nBit", "Level": (2,), "Priority": ("M",)},
                                {"Key": "R/W\nProperty", "Level": (2,), "Priority": ("M",)},
                                {"Key": "Register\nName", "Level": (1, 2), "Priority": ("M", "M")},
                                {"Key": "Register Description", "Level": (1, 2), "Priority": ("L", "L")}]
        self._dev_dic_reheader = ("Address", "Start", "End", "Property", "Name", "Description")
        # Reference list indicate the excel sheet row belong to which level
        self._dev_ref_list = []
        for _ in range(max(tuple(j for i in self._dev_dic_header for j in i["Level"]))):
            self._dev_ref_list.append([])
        for i in self._dev_dic_header:
            for level, priority in zip(i["Level"], i["Priority"]):
                self._dev_ref_list[int(level) - 1].append(priority)

        self._convert()

    def _locate_key(self, sheet, header):
        for f_num, dct in enumerate(header):
            for col, cell in enumerate(sheet.row(0)):
                if dct["Key"] == cell.value:
                    if "Col" in header[f_num].keys():
                        header[f_num]["Col"] = col
                    else:
                        header[f_num].update({"Col": col})
                    break
            else:
                # Not locate the key
                return False
        return True

    def _convert(self):
        # Generate Device list
        for sheet in self.dtc_dic:
            handler = self._xlrd_handler.sheet_by_name(sheet)

            # Locate the column
            if not self._locate_key(handler, self._dtc_dic_header):
                raise ValueError("Excel format error")

            rows = handler.get_rows()

            # Ignore the first row
            next(rows)

            # Generate
            for row in rows:
                para = {}
                for dtc, redtc, num in zip(self._dtc_dic_header, self._dtc_dic_reheader,
                                           range(max(len(self._dtc_dic_header), len(self._dtc_dic_reheader)))):
                    para.update({redtc: row[dtc["Col"]].value})
                self._device.append(HalDevice(**para))

        # Generate Device class list
        for sheet in self.dev_dic:
            handler = self._xlrd_handler.sheet_by_name(sheet)

            _device = HalDeviceClass(sheet)
            _regiser = None
            _filed = None
            _para = {}

            # Locate the column
            if not self._locate_key(handler, self._dev_dic_header):
                raise ValueError("Excel format error")

            rows = handler.get_rows()

            next(rows)

            for row in rows:
                for i in zip(self._dev_dic_header, self._dev_dic_reheader):
                    _para.update({i[1]: row[i[0]["Col"]].value})

                level = self._state_machine_level_check(row, self._dev_dic_header)
                # regiser
                if level == 1:
                    _regiser = Register(**_para)
                    _device.add_regiser(_regiser)

                elif level == 2:
                    _filed = Filed(**_para)
                    _regiser.add_filed(_filed)

            _device.is_end()
            self._deviceclass.append(_device)

        # Combine the device list and device class list
        for dev in self._device:
            for devc in self._deviceclass:
                if dev.device_class_name == devc.device_class_name:
                    dev.add_device_class(devc)

        self._strip()

        sorted(self._device, key=HalDevice.get_device_addr)

    # In level check machine, have 3 priority for each level
    # High, Middle, Low
    # High priority, indicate this row belong corresponding level immediately
    # Middle, normal priority, the column must have, but not immediately confirm this row belong corresponding level
    # Low, level need this column data but this column will not influence corresponding row belong which level
    # 核心思想：发现同级别的数据单元时，将栈中同级的数据块填写到上一级块中的缓存单元中
    # eg：当前到Level2，又发现一个符合Level2的单元时，将当前的Level2压入上一层的Level1中的Level list中
    # The excel like below:
    # Level 1
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #   Level 2
    #       Level 3
    #   Level 2
    #       Level 3
    #       Level 3
    #       Level 3
    #       Level 3
    def _state_machine_level_check(self, row, header):
        # A temporary list
        rslt_list = []
        for _ in range(max(tuple(j for i in header for j in i["Level"]))):
            rslt_list.append([])

        # Add each level column into their stack
        for dct in header:
            for j, p in zip(dct["Level"], dct["Priority"]):
                # corresponding cell have value
                if row[dct["Col"]].value != "":
                    rslt_list[int(j) - 1].append(p)
                else:
                    rslt_list[int(j) - 1].append(None)

        # According to flow chart to indicate current row belong which level
        for rslt, ref, num in zip(rslt_list, self._dev_ref_list, range(len(rslt_list))):
            if self._sub_state_machine_level_check(rslt, ref):
                return num + 1

    def _sub_state_machine_level_check(self, rslt, ref):
        ret = True
        for s, f in zip(rslt, ref):
            if not s:
                if f == "H":
                    return False
                elif f == "M":
                    ret &= False
                elif f == "L":
                    pass
                else:
                    raise ValueError("Level state machine trigger error")
            else:
                if f == "H":
                    return True
                elif f == "M":
                    ret &= True
                elif f == "L":
                    ret &= True
                else:
                    raise ValueError("Level state machine trigger error")

        return ret

    def _strip(self):
        temp = []
        for item in self._device:
            if not item.device_class:
                temp.append(item)

        for item in temp:
            self._device.remove(item)

    def __iter__(self):
        return iter(self._device)


if __name__ == "__main__":
    handler = PeripheralRegisterParser("test.xls", ["AP Peripheral AddrMapping", "CP Peripheral AddrMapping"],
                                       exclude=["SysAddrMapping"])

    for device in handler:
        print("[Device]-->", device())
        for register in device:
            print("[Register-->]", register())
            for filed in register:
                print("[Filed]-->", filed())
