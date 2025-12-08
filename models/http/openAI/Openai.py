# Openai.py 开头添加这 2 行
import sys
from pathlib import Path
import time
import numpy as np
import copy
# 获取 models 目录的父目录（即 log 和 models 所在的根目录）
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from openai import OpenAI
from models.template.Qwen3 import aluminum_electrolysis_question,get_message,extract_id_and_content
from models.http.HttpBaseInstance import HttpChatInstance,BaseHttpInstance

knowledge_seg = [{"name":"铝电解迈向零碳排放的道路.pdf","content":"研究结果表明，阳极在使用前必须均质化，才能有 更好的耐腐蚀性。\nSolheim认为：从经济和环境方面来看，惰性 阳极铝电解槽与传统霍尔-埃鲁铝电解槽相比较没 有显著的优势。2015年铝电解生产的单位能耗从 2006年的14.286kWh/kg-Al 降低到13.403kWh/kg-Al。\n由于较高的可逆电压，惰性阳极铝电解槽的单位能 耗为15.35kWh/kg-Al，高出传统霍尔-埃鲁铝电解 槽15%以上。因此，惰性阳极的优点只有在用于 电解过程的电能来自于可再生能源时才是有益 的。\n避免这种能量消耗增加可能的方法是将惰性 阳极铝电解槽设计为一个垂直电极的铝电解槽 （VEC），而不是像霍尔-埃鲁铝电解槽一样使用水 平阳极，避免由于液体金属运动和波动导致的复杂 因素出现，液体金属是工业铝电解槽的实际阴极。\nVEC的配置要求使用能够被熔融铝湿润的阴极， TiB2是目前适合该应用的最佳材料。覆盖湿润阴极 的薄铝膜能够缩短阴-阳极距离，降低铝电解槽的 欧姆电阻，增加这一昂贵电极的电活性区域，这样 阳极表面上产生的气泡可以很容易地从活性电解"}
                 ,{"name": "铝电解迈向零碳排放的道路.pdf","content":"排放的主要部分是间接排放，在电解各步 骤需要使用的电能中释放，估计平均为 9.6tCO2eq/t-Al，这些排放物高度依赖于能源，从实 践经验来看，其跨度可从全部使用可再生能源的零 排放到使用劣质煤炭发电的高达12~18tCO2eq/t-Al 的排放量。\n目前，正在努力降低氧化铝生产和阳极生产所 产生的排放，但本文重点讨论的是霍尔-埃鲁电解 工艺本身以及减少此工艺排放的问题。下表1列出 了全球铝电解平均排放量以及���用最佳技术 （BAT）实现的最低排放量，采用2021年的能源 数据。\n减少或消除铝电解过程排放的努力现可分为 三类，一类是有许多倡议旨在用非消耗性析氧阳极 或惰性阳极取代碳阳极；另一类是从霍尔-埃鲁电 解烟气中捕获CO2进行隔离和/或利用；第三类是 氧化铝与碳和氯的反应形成AlCl3，然后在熔融的 氯化物电解液中电解。\n然而，如果不解决所使用电能的间接排放问\n解生产过程中使用的能源组合发展以及未来机会 等问题也在此进行了讨论。\n铝电解减少排放的途径\n析氧惰性阳极\n铝电解生产过程中获得零排放的一个有影响 力的方面，就是在铝电解槽中采用析氧惰性阳极代 替可消耗的碳阳极。铝电解工艺采用惰性阳极可以 消除或最小化温室气体排放，降低与生产相关的操 作成本，避免频繁更换碳阳极，并提高铝电解槽的 单位生产率。然而，寻找一种合适的且可以在高温 下承受电解质腐蚀的阳极材料一直具有挑战性，探 索仍在进行中。目前，主要研究了三种惰性阳极材 料：金属、陶瓷和金属陶瓷。金属阳极通常是由两 种或两种以上的金属组成的合金，具有良好的导电 性、抗热冲击能力和易于制造的特性，但容易发生 严重腐蚀。陶瓷是一种高耐腐蚀性的金属氧化物， 在化学上是惰性的，但导电性能较差。金属陶瓷是 金属和陶瓷的结合，具有良好的导电性、低的熔解 率和高的化学惰性。有关文献对这些材料类型有一 个很好的概述。"},
                   {"name":"铝电解迈向零碳排放的道路.pdf","content":"质区域逸出。\n然而，始终应向铝电解槽提供足够的电压来满 足反应焓（EΔH=2.9）以及任何其他的热损失的需 要。如果槽电压保持在4V左右，就像正常的霍尔 -埃鲁铝电解槽一样，惰性阳极铝电解槽的热损失 必须小于50%，以保持电解质的温度，这就带来 了一个挑战，就是需要在铝电解槽的侧部维持一层 保护内衬的炉帮。由于VEC铝电解槽可以设计得 更加紧凑，每台槽容量具有更高的电流，铝电解槽 的较小表面积可以帮助解决这个问题。\nElysis 正在研发一种VEC技术，该技术计划 于2024年前进行商业化应用。有关人员指出惰性 阳极的寿命为2.5年（比碳阳极的寿命长30倍）， 操作成本将比传统铝电解槽低15%。\nArctus金属公司和IceTech公司也正在进行一 种基于Fe、Ni 和Cu的合金金属阳极的VEC技术 设计。事实上，在上述三种材料类型中，金属已经 得到了广泛的研究，并被认为是惰性阳极铝电解槽 中阳极的有应用前景的候选材料。金属可以在电解 过程中形成保护性氧化层，保护阳极免受氧气和电 解质的渗透，延长其使用寿命。研究结果表明，阳 极在使用前必须均质化，这样才能有更好的耐腐蚀 性。阳极也可以通过预氧化来保护自身不受腐蚀和 氟化。另一种方法是使用电沉积或气相沉积工艺用 保护层覆盖阳极。一个例子是De Nora 阳极，由 镍铁基合金制成，并在阳极表面镀上钴基涂层，以 延长阳极寿命。阳极在100-300kA的铝电解槽中 进行试验测试，结果表明，阳极的寿命为1年，氧 化层熔解的速率约为3毫米/年。"},
                    {"name":"铝电解迈向零碳排放的道路.pdf","content":"<table><caption>表1全球铝电解排放数据，平均排放量以及使用最佳技术（BAT）在铝电解厂可实现的最低CO2当量排放，根据有关文献得出的数据（3）（4）</caption>\n<tr><th  >CO2 当量 排放 工艺</th><th  >中国平均 （tCO2eq/t-Al）</th><th  >中国以外 （tCO2eq/t-Al）</th><th  >全球平均 （tCO2eq/t-Al）</th><th  >使用最佳技术 （tCO2eq/t-Al）</th></tr>\n<tr><td  >发电</td><td  >12.4 </td><td  >4.6 </td><td  >9.6 </td><td  >0</td></tr>\n<tr><td  >电解</td><td  >1.5 </td><td  >1.5 </td><td  >1.5 </td><td  >1.4</td></tr>\n<tr><td  >形成 PFC 排出</td><td  >1.12 </td><td  >0.19 </td><td  >0.75 </td><td  >0.13</td></tr>\n<tr><td  >辅助 材料</td><td  >0.1 </td><td  >0.1 </td><td  >0.1 </td><td  >0.1</td></tr>\n<tr><td  >运输</td><td  >0.3 </td><td  >0.3 </td><td  >0.3 </td><td  >0.3</td></tr>\n<tr><td  >总计</td><td  >15.4 </td><td  >6.7 </td><td  >12.2 </td><td  >1.9</td></tr>\n</table>"},
                    {"name":"铝电解槽热平衡基础和应用.pdf","content":"氧化铝实质上视为相，而碳可以被认为是石墨的，产品则为液态金属和气态二 氧化碳。在这种情况下，该反应是吸热的，因此需要能量添加到体系中。\n需要注意的是，我们使用反应热焓能量定义来确定反应所需的最小能量来替 代吉布斯自由能。这是因为有熵的存在（例如，气态产物），所以，自由能低于 热焓，根据下列反应式可以看出热焓高于自由能：\nH=G+TS \n(1—2)\n在实际电解过程中，存在有电流效率的损失，主要是二次反应，即CO2 与溶 解的金属反应生成CO。根据电解温度条件下的表达式总（1-1），其完整的化\n1\n学反应式应为（1-3）式。\n1.2 关于A氧l2O化3 铝+与3炭还C原→的2A完l +整3化2学−反1应C式O或2 +电3 解1铝−的1 总C反O 应式的(推1导−\n沈时英在《再2谈x 铝电解的能2 量问题x 》[1]中对式（x ）作了极为详细的4)1-4推导， 从而为准确的计算能量平衡和热平衡奠定了基础，这是他很重要的一份贡献。\n在铝电解的能量需求的方程式中，有两种表述方式：\n一种是以气体组成为系数的表达方式：\n式中：Al2NO=3 C+O2 /C3O+CCO→2是2体Al 积+比。"},
                    {"name":"铝电解槽热平衡基础和应用.pdf","content":"1.3 炭还原氧化铝的热力学计算或能量的需求\n计算铝电解能量需求的计算基础是前述的化学反应式（1-4），该式是按照 2Al 列出的。为了简化技术，我们把式（1-4）改成1Al 的方程式，如式（1-12）。\n1在A计l2O算3 式+（1-12C）→时A，l 还+应该2考−虑把CO物2 料+从3室1温−提1 高CO 到电解温度所(1需−要]"}
                    ]

class ChatInstanceByOpenai(HttpChatInstance):
    def __init__(self,http_url:str,api_key:str):
        super().__init__(http_url=http_url,api_key=api_key)
        self.content_list = []
        self._client = None
        self._client = self.create_instance()
        self.stream = None
        self.content = ""
        pass
    def create_instance(self):
        if self._client is not None:
            return self._client
        client = OpenAI(api_key=self.api_key,base_url=self.http_url)
        return client

    def push_content_segment(self,document:str,content:str):
        cont = {"name":document,"content":content}
        self.content_list.append(cont)

    def push_content_segments(self,sge:list):
        for seg in sge:
            self.push_content_segment(seg["name"],seg["content"])

    def question(self,question:str,history_conversation_list:list,stream:bool):
        history = copy.deepcopy(history_conversation_list)
        self.content = get_message("铝电解","",self.content_list)
        history += aluminum_electrolysis_question(question,self.content)
        message = history
        stream = self._client.chat.completions.create(model="Qwen3-8B",frequency_penalty=0.5,presence_penalty=0.5,temperature=0.2,top_p=0.75,
                               messages=message,stream=stream)
        self.stream = stream

    def get_content(self) -> list:
        return extract_id_and_content(self.content)
    
    def response(self):
        for chunk in self.stream:
            content = chunk.choices[0].delta.content
            yield content


class EmbeddingInstanceByOpenai(BaseHttpInstance):
    def __init__(self, http_url, api_key,embedding_model:str):
        super().__init__(http_url, api_key)
        self.client:OpenAI = None
        self.client = self.create_instance()
        self.embedding_model = embedding_model
    def create_instance(self):
        if self.client is not None:
            return self.client
        client = OpenAI(api_key=self.api_key,base_url=self.http_url)
        return client
    def _create_embedding_model_instance(self,text):
        texts = text
        if isinstance(texts,str):
            texts = [text]
        try:
            response = self.client.embeddings.create(input = texts,model=self.embedding_model)
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            print(f"发生错误:{e}")
            return []
    
    def cosine_similarity(self,vec1,vec2):
        """计算两个向量的余弦相似度，取值[-1,1]，越接近1关联度越高"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        # 避免除以0（向量全0时相似度为0）
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def calculate_relevance(self,question:str,keywords:list):
        question_embedding_vec = None
        question_embedding = self._create_embedding_model_instance(question)
        question_embedding_vec = question_embedding[0]
        keywords_embedding = self._create_embedding_model_instance(keywords)

        # 步骤3：计算每个关键字的关联度
        results = []
        for idx, keyword in enumerate(keywords):
            relevance = self.cosine_similarity(question_embedding_vec, keywords_embedding[idx])
            relevance_rounded = round(relevance, 3)
            # 定义匹配等级（可自定义阈值）
            results.append({
                "key": keyword,
                "relevance": relevance_rounded,
            })
        # 按关联度降序排序
        return sorted(results, key=lambda x: x["relevance"], reverse=True)


# start = time.time()
# chat = ChatInstanceByOpenai(http_url="http://192.168.5.208:8007/v1",api_key="")
# chat.push_content_segments(knowledge_seg)
# chat.question("什么是铝电解?",True)
# for chunk in chat.response():
#     print(chunk,end="",flush=True)
# end = time.time()

# print(f"开销:{end - start}")

# embeddding = EmbeddingInstanceByOpenai(http_url="http://192.168.5.208:8006/v1",api_key="",embedding_model="Qwen3-Embedding")
# print(embeddding.calculate_relevance("阳极棒容易被氧化，如何提升阳极棒效率?",["工艺","基础","铝电解"]))