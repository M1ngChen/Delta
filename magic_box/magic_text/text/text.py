# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from magic_box.magic_text.base_text import BaseText
from typing import List
import random


class ExtractText(BaseText):
    def __init__(self,start:str,end:str,regex:str):
        super().__init__()
        self.start:str = start
        self.end:str = end
        self.regex:str = regex
        self.assistant_dict = {}
        self.assistant_list = []
        self.current_paragraph:int = 0
        self.assistant_paragraph = [[]]
        self._tmp_str_ = ""
        self._extract_imp = ""
        self._start_flag:bool = False
    
    def _create_instance(self):
        return super()._create_instance()
    
    def _find(self,string:str):
        start = None
        end = None
        index = 0
        for char in string:
            if char == self.end:
                end = index
            if char == self.start:
                start = index
            index = index + 1
        return (start,end)
    def _get_import_info(self,imp:str) -> int | None:
        if "ID" not in imp:
            return None
        print(imp)
        return int(imp[4:len(imp) -1])

    def _find_line_break(self,string:str) -> bool:
        if "\n\n" in string:
            return True
        return False

    def _dynamic_text_paragraph_gen(self,d:dict):
        for key,value in d.items():
            if self._find_line_break(value):
                self.assistant_paragraph.append([])
                self.current_paragraph += 1
            self.assistant_paragraph[self.current_paragraph].append(d)

    def _extract_care(self,string:str) -> (None | str):
        tup = self._find(string)
        if tup[0] == None and tup[1] == None:
            self._tmp_str_ += string
            if self._start_flag:
                self._extract_imp += string
            return None
        if tup[0] is not None and tup[1] == None:
            if self._extract_imp != "":
                self._extract_imp = ""
            self._tmp_str_ += string
            self._extract_imp += string[tup[0]:]
            self._start_flag = True
            return None
        if tup[0] is None and tup[1] is not None:
            self._tmp_str_ += string[:tup[1] + 1]
            self._extract_imp += string[:tup[1] + 1]
            self._start_flag = False
            index = self._get_import_info(self._extract_imp)
            if index is not None:
                index = str(index)
                if not self.assistant_dict.get(index):
                    self.assistant_dict[index] = []
                self.assistant_dict[index].append(self._tmp_str_)
                self.assistant_list.append({f"{index}":self._tmp_str_})
                self._dynamic_text_paragraph_gen({f"{index}":self._tmp_str_})
                self._tmp_str_ = ""
                self._extract_imp = ""
                return index
            else:
                self._extract_imp = ""
                return None
        if tup[0] is not None and tup[1] is not None:
            self._tmp_str_ += string[:tup[1] + 1]
            self._extract_imp += string[tup[0]:tup[1] + 1]
            self._start_flag = False
            index = self._get_import_info(self._extract_imp)
            if index is not None:
                index = str(index)
                if not self.assistant_dict.get(index):
                    self.assistant_dict[index] = []                
                self.assistant_dict[index].append(self._tmp_str_)
                self.assistant_list.append({f"{index}":self._tmp_str_})
                self._dynamic_text_paragraph_gen({f"{index}":self._tmp_str_})
                self._tmp_str_ = ""
                self._extract_imp = ""
                if len(string) - 1 > tup[1]:
                    self._tmp_str_ += string[tup[1]+1:]
                return index
            else:
                self._extract_imp = ""
                return None
    def push_string(self,string:str):
        ret = self._extract_care(string)

    def get_current_paragraph(self,index) -> list:
        if index > self.current_paragraph:
            return []
        return self.assistant_paragraph[index]

    def get_all_paragraph(self) -> List[list]:
        return self.assistant_paragraph

    def get_current_generated_text_list(self) -> list:
        return self.assistant_list

    def get_all_text(self) -> dict:
        return self.assistant_dict

    def get_all_text_by_index(self,index) -> list:
        if self.assistant_dict.get(str(index)):
            return self.assistant_dict[str(index)]
        return []
    
    # def printf(self):
    #     print(self.assistant_dict)

    # def printf_paragraph(self):
    #     for seg in self.assistant_paragraph:
    #         print(f"当前段落:{seg} \n\n\n")


# strs = """铝电解工艺涉及多个关键技术和参数优化。首先，阳极在使用前必须均质化以提高耐腐蚀性[ID:0]，而惰性阳极铝电解槽因较高的可逆电压导致单位能耗比传统霍尔-埃鲁槽高15%以上（15.35kWh/kg-Al vs 13.403kWh/kg-Al）[ID:0]。这种能量消耗增加仅在电能来自可再生能源时才具优势[ID:0]。

# 铝电解的能量需求基于炭还原氧化铝的热力学计算，需考虑将碳材料从室温加热至电解温度（约977℃）所需的焓变[ID:2]。完整的化学反应式为Al₂O₃ + C → 2Al + CO₂，并需额外补偿二次反应（如CO₂与金属反应生成CO）造成的能量损失[ID:3]。

# 电解槽设计对能耗影响显著：垂直电极配置（VEC）通过缩短阴-阳极距离降低欧姆电阻，采用TiB₂湿润阴极可扩大电活性区域[ID:0]。电流效率通常介于90%-95%之间，直接影响单位能耗（DCkWh/kg）[ID:1]。此外，电解槽运行电压与热能需求的关系为±Q = nF*[E±+n±] [ID:4]。

# 工艺优化需关注：①原料杂质控制（如氧化铝含≥6%Al₂O₃·H₂O）[ID:4]；②通过调整电流密度实现电位调控[ID:4]；③维持质量平衡（连续供料与出铝）和能量平衡[ID:4]。这些因素共同决定了铝电解的经济性和环境效益。"""



# def broken_string(string:str) -> list:
#     ret_list = []
#     total_use = 0
#     _len = len(string)
#     while True:
#         if total_use >= _len:
#             break
#         cur_use = _len - total_use
#         size = random.randint(1,5)
#         if cur_use < size:
#             size = cur_use
#         if total_use == 0:
#             _str = string[total_use : total_use + size - 1]
#         else:
#             _str = string[total_use - 1 : total_use + size - 1]
#         ret_list.append(_str)
#         total_use += size
#     return ret_list

# l = broken_string(strs)
# print("\n\n\n")
# print("############################################################")
# print(l)
# print("############################################################")
# print("\n\n\n")
# ext = ExtractText("[","]","")
# for s in l:
#     ext.push_string(s)
# # ext.printf()
# print("\n\n\n")
# ext.printf_paragraph()