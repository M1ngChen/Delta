import re


Prompt_tail = f"\n\n\nBased on the provided document or chat history, add citations to the input text using the format specified later. \n\n# Citation Requirements:\n\n## Technical Rules:\n- Use format: [ID:i] or [ID:i] [ID:j] for multiple sources\n- Place citations at the end of sentences, before punctuation\n- Maximum 4 citations per sentence\n- DO NOT cite content not from <context></context>\n- DO NOT modify whitespace or original text\n- STRICTLY prohibit non-standard formatting (~~, etc.)\n\n## What MUST Be Cited:\n1. **Quantitative data**: Numbers, percentages, statistics, measurements\n2. **Temporal claims**: Dates, timeframes, sequences of events  \n3. **Causal relationships**: Claims about cause and effect\n4. **Comparative statements**: Rankings, comparisons, superlatives\n5. **Technical definitions**: Specialized terms, concepts, methodologies\n6. **Direct attributions**: What someone said, did, or believes\n7. **Predictions/forecasts**: Future projections, trend analyses\n8. **Controversial claims**: Disputed facts, minority opinions\n\n## What Should NOT Be Cited:\n- Common knowledge (e.g., \"The sun rises in the east\")\n- Transitional phrases\n- General introductions\n- Your own analysis or synthesis (unless directly from source)\n\n# Comprehensive Examples:\n\n## Example 1: Data and Statistics\n<context>\nID: 45\n└── Content: The global smartphone market grew by 7.8% in Q3 2024, with Samsung holding 20.6% market share and Apple at 15.8%.\n\nID: 46  \n└── Content: 5G adoption reached 1.5 billion users worldwide by October 2024.\n</context>\n\nUSER: How is the smartphone market performing?\n\nASSISTANT: \nThe smartphone industry is showing strong recovery. The global smartphone market grew by 7.8% in Q3 2024 [ID:45]. Samsung leads with 20.6% market share, followed by Apple at 15.8% [ID:45]. This growth is partly driven by 5G technology, which reached 1.5 billion users worldwide by October 2024 [ID:46].\n\n## Example 2: Causal Relationships and Predictions\n<context>\nID: 78\n└── Content: Rising interest rates have led to a 15% decline in housing starts. Economists predict this trend will continue through 2025.\n\nID: 79\n└── Content: The Federal Reserve's aggressive monetary policy is the primary driver behind the real estate slowdown.\n</context>\n\nUSER: What's happening in the real estate market?\n\nASSISTANT:\nThe real estate market is experiencing significant challenges. Rising interest rates have led to a 15% decline in housing starts [ID:78]. The Federal Reserve's aggressive monetary policy is the primary driver behind this real estate slowdown [ID:79]. Economists predict this trend will continue through 2025 [ID:78]. These factors suggest a prolonged period of market adjustment ahead.\n\n## Example 3: Technical Concepts and Comparisons\n<context>\nID: 101\n└── Content: Quantum computing uses quantum bits (qubits) that can exist in superposition, unlike classical bits which are either 0 or 1.\n\nID: 102\n└── Content: Current quantum computers can solve certain problems 158 million times faster than classical supercomputers.\n</context>\n\nUSER: Explain quantum computing advantages.\n\nASSISTANT:\nQuantum computing represents a fundamental shift in computational capability. Unlike classical computers, quantum computing uses quantum bits (qubits) that can exist in superposition, rather than being limited to just 0 or 1 [ID:101]. This unique property enables extraordinary performance gains. Current quantum computers can solve certain problems 158 million times faster than classical supercomputers [ID:102]. This technology promises to revolutionize fields requiring complex calculations.\n\n## Example 4: Mixed Citation Needs\n<context>\nID: 201\n└── Content: CEO Jane Smith announced: \"We're pivoting to AI-first strategy, expecting 40% revenue growth by 2026.\"\n\nID: 202\n└── Content: Industry analysts remain skeptical, with Morgan Stanley rating the stock as \"underperform.\"\n\nID: 203\n└── Content: The company's AI division currently represents only 5% of total revenue.\n</context>\n\nUSER: What's the company's new strategy?\n\nASSISTANT:\nThe company is undergoing a major strategic transformation. CEO Jane Smith announced: \"We're pivoting to AI-first strategy, expecting 40% revenue growth by 2026\" [ID:201]. However, this ambitious goal faces skepticism, as industry analysts remain doubtful, with Morgan Stanley rating the stock as \"underperform\" [ID:202]. The challenge is significant given that the company's AI division currently represents only 5% of total revenue [ID:203]. Success will depend on execution of this bold vision.\n\n## Example 5: When NOT to Cite\n<context>\nID: 301\n└── Content: Paris is the capital of France. The Eiffel Tower was completed in 1889.\n</context>\n\nUSER: Tell me about Paris.\n\nASSISTANT:\nParis is the capital of France. It's known for its rich history, culture, and architecture. The Eiffel Tower was completed in 1889 [ID:301]. The city attracts millions of tourists annually. Paris remains one of the world's most visited destinations.\n(Note: Only the specific date needs citation, not common knowledge about Paris)\n\n--- Examples END ---\n\nREMEMBER: \n- Cite FACTS, not opinions or transitions\n- Each citation supports the ENTIRE sentence\n- When in doubt, ask: \"Would a fact-checker need to verify this?\"\n- Place citations at sentence end, before punctuation\n- Format likes this is FORBIDDEN: [ID:0, ID:5, ID:...]. It MUST be seperated like, [ID:0][ID:5]..."

def create_prompt(professional,content) -> str:
    prompt_header = Prompt_header = f"你是一个{professional}方面的专家，针对用户的提问结合下述知识库的片段内容进行专业的回答，不要编造任何和知识库内容无关的信息。相关链接如果不是来自知识库的，请不要包含在回答中。{content}"
    return prompt_header
def create_new_knowledge_content(index:int,source_name:str,content:str) -> str:
    knowledge_seg = f"\n------\n\nID: {index}\n├── Title: {source_name}\n└── Content:\n\n{content}"
    return knowledge_seg

def get_message(professional,content:str,knowledge_seg:list) -> str:
    ret_content = ""
    ret_content = ret_content + create_prompt(professional,content)
    ret_content = ret_content + "Here is the knowledge base:"
    index = 0
    for seg in knowledge_seg:
        ret_content = ret_content + create_new_knowledge_content(index,seg["name"],seg["content"])
        index = index + 1
    ret_content = ret_content + Prompt_tail
    return ret_content

def aluminum_electrolysis_question(question:str,knowledge_seg:str):
    return [
            {"role":"system",
             "content":knowledge_seg},
            {"role":"user",
              "content":question
            }
    ]

def extract_id_and_content(text: str) -> list[dict]:
    """
    从指定格式的字符串中提取index和content，返回list[dict]
    
    参数：
        text: 待处理的原始字符串，包含多个------分隔的条目
    返回：
        list[dict]: 每个字典包含 'index'（字符串/整数）和 'content'（字符串）键
    """
    # 最终结果列表
    result = []
    
    # 步骤1：按分隔符------分割字符串，过滤空条目
    # 先替换换行符为统一格式，再分割，避免换行符数量不一致导致的问题
    normalized_text = text.replace("\r\n", "\n").strip()
    # 按------分割，分割后过滤空字符串（处理首尾/连续分隔符）
    entries = [entry.strip() for entry in re.split(r"\n\-{5,}\n", normalized_text) if entry.strip()]
    
    # 步骤2：遍历每个条目，提取index和content
    for entry in entries:
        # 初始化当前条目的结果
        item = {"index": "", "content": ""}
        
        # 提取ID（匹配 ID: 任意字符 格式，非贪婪匹配）
        id_match = re.search(r"ID:\s*(\S+)", entry)
        if id_match:
            index_str = id_match.group(1)
            # 尝试将index转为整数（如果是数字），否则保留字符串
            try:
                item["index"] = int(index_str)
            except ValueError:
                item["index"] = index_str
        
        # 提取Content（匹配 Content: 之后的所有内容）
        # 先找到Content:的位置，再截取后续内容
        content_match = re.search(r"Content:\s*\n\s*(.*)", entry, re.DOTALL)
        if content_match:
            # 清理content首尾的空白，保留中间的格式
            content = content_match.group(1).strip()
            item["content"] = content
        
        # 仅当index或content非空时添加（避免空条目）
        if item["index"] or item["content"]:
            result.append(item)
    
    return result



