import re, string, copy

class SplitFormular:
    
    def __init__(self, ratio_sums_cands=[]):
        self.ratio_sums_cands = ratio_sums_cands
    
    def split_formulars(self, formular_data, output=dict):
        """


        Parameters
        ----------
        formular_data : LIST
            contains string formulars.

        Returns
        -------
        splited_formulars and unsplited_formualrs.

        """
        splited_formulars = []
        unsplited_formulars = []
        
        for index in range(len(formular_data)):
            formular = formular_data[index]
            try:
                splited_formular = self.split_formular(formular)
            
                ratio_sums_cand_i = 0
                while isinstance(splited_formular, str) and ratio_sums_cand_i < len(self.ratio_sums_cands):
                    splited_formular = self.split_formular(formular, self.ratio_sums_cands[ratio_sums_cand_i])
                    ratio_sums_cand_i += 1
                if isinstance(splited_formular, list):
                    if output == dict:
                        splited_formulars.append(splited_formular)
                    elif output == str:
                        output_str = ""
                        for i in splited_formular:
                            for j, k in i.items():
                                output_str += str(j)
                                if float(k) != 1:
                                    output_str += str(k)
                        splited_formulars.append(output_str)
                else:
                    unsplited_formulars.append(splited_formular)
            except:
                unsplited_formulars.append(formular)
        return splited_formulars, unsplited_formulars
    
    def split_formular(self, formular, ratio_sums=[1, 1, 3]):
        
        formular_list = self._split_formular(formular)
        
        site_list = [ {} for i in range(len(ratio_sums)) ]
        
        formular_i = 0
        site_i = 0
        ratios = 0
        while formular_i < len(formular_list):
            _formular = formular_list[formular_i]
            ratio_sum = ratio_sums[site_i]
            ratio = re.compile("[\d+\.]+").findall(_formular)[0]
            ele = _formular.split(str(ratio))[0]
            ratios += float(ratio)
            site_list[site_i].update({ele:ratio})
            
            if round(ratios, 10) == round(ratio_sum, 10):
                site_i += 1
                ratios = 0
            formular_i += 1
        if len(site_list[1]) == 0 or len(site_list[2]) == 0:
            return formular
        return [ self._sortdict(i) for i in site_list ]
        
    def _sortdict(self, adict,reverse=False):
        keys = list(adict.keys())
        keys.sort(reverse=reverse)
        return {key:adict[key] for key in keys}
    
    def _translate(self, _string, addition=[]):
    
        string_punctuation = string.punctuation
        string_punctuation = string_punctuation.translate(str.maketrans("", "", "."))
        
        if len(addition) == 0:
            translation_str = string_punctuation
        else:
            translation_str = string_punctuation + "".join(addition)
        
        translate_table = str.maketrans("", "", translation_str)
        
        return _string.translate(translate_table)
    
    def _split_formular(self, formular):
        # print(formular)
        formular = self._translate(formular)
        ratios = re.compile("[\d+\.]+").findall(formular)
        splited_parts_by_ratios = re.split("|".join(ratios), formular)
        if not self.check_split_parts_by_ratio(splited_parts_by_ratios):
            splited_parts_by_ratios = self.split_parts_by_compatiability(formular, ratios)
        parts_with_ratios_list = []
        for ratio, part in zip(ratios+["1"], splited_parts_by_ratios):
            
            if len(part) == 0 or part == " ":
                continue
            
            subparts = re.compile("[A-Z]{1,2}(?![a-z])|[A-Z]{1}[a-z]{1,2}|[A-Z]{3}(?![a-z])|(?<=[N])[WVYP]").findall(part)
            
            if len(subparts) > 1:
                for i,j in enumerate(subparts[:-1]):
                    subparts[i] = subparts[i] + "1"
            # print(part)
            subparts[-1] = subparts[-1] + ratio
            
            parts_with_ratios_list += subparts
        
        organic_part = ["".join([ i for i in parts_with_ratios_list if re.compile("[CHNOP](?![a-z])").findall(i)])]
        inorganic_part = [ i for i in parts_with_ratios_list if not re.compile("[CHNOP](?![a-z])").findall(i)]
        if len(organic_part) == 0 or organic_part[0] == "" or organic_part[0] == " ":
            splited_formular_list = inorganic_part
        else:
            splited_formular_list = organic_part + inorganic_part
        
        return splited_formular_list
    
    def check_split_parts_by_ratio(self, x):
        for i in x:
            part = re.compile("[\d+\.]+").findall(i)
            if len(part) == 0:
                continue
            else:
                part = part[0]
            try:
                float(part)
                return False
            except:
                pass
        return True
    
    def split_parts_by_compatiability(self, _formular, ratios):
        formular = copy.deepcopy(_formular)
        formular_list = list()
        for r in ratios:
            site = re.split(r, formular)[0] + r
            formular_list.append(site)
            site_len = len(site)
            formular = formular[site_len:]
        return formular_list
        
    def abcsites(self, formulars):
        splited_formulars, unsplited_formulars = self.split_formulars(formulars)
        a_sites = []
        b_sites = []
        c_sites = []
        for split_formular in splited_formulars:
            for site_l, index in zip([a_sites, b_sites, c_sites], range(len(split_formular))):
                for i, j in split_formular[index].items():
                    site_l.append(i)
        return [list(set(a_sites)), list(set(b_sites)), list(set(c_sites))]

# if __name__ == "__main__":
    
#     from fml.dataobject import ReadData
    
#     PL = ReadData(r"C:\Users\luktian\OneDrive\钙钛矿数据处理\处理09-20年数据的带隙值\只含有有效带隙值的数据.xlsx")().to_df().PL.values.tolist()
#     sf = SplitFormular()
#     a, b = sf.split_formulars(PL)
