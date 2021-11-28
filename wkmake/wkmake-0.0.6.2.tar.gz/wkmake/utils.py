
class Parser:
    def __init__(self,line_split='\n',pair_split='=',comment_tags=['#',';']):
        self.line_split=line_split
        self.pair_split=pair_split
        self.comment_tags=comment_tags
    def parse_line(self,line):
        dic={}
        if not line.strip(): return dic
        is_comment = False
        for tag in self.comment_tags:
            if line.strip().startswith(tag):
                is_comment = True
                break
        if is_comment: return dic
        line = line.strip()
        key, value = line.split(self.pair_split, maxsplit=1)
        key = key.strip()
        value = value.strip()
        dic[key] = value
        return dic
    def parse(self,text=''):
        lines=text.strip().split(self.line_split)
        dic = {}
        for line in lines:
            dic.update(self.parse_line(line))
        return dic
def load_simple_config(fp,line_split='\n',pair_split='=',encoding="utf-8",comment_tags=['#',';']):
    '''
    a=1
    b=2
    '''
    with open(fp,'r',encoding=encoding) as f:
        lines=f.read().strip().split(line_split)
        dic={}
        for line in lines:
            if not line.strip():continue
            is_comment=False
            for tag in comment_tags:
                if line.strip().startswith(tag):
                    is_comment=True
                    break
            if is_comment:continue
            line=line.strip()
            key,value=line.split(pair_split,maxsplit=1)
            key=key.strip()
            value=value.strip()
            dic[key]=value
        return dic

def export(src,dst):
    import shutil
    shutil.copytree(src,dst,)
