import json
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.llm import LLMModel
from utils.rag_sql import RAGDatabase
from utils.voice import generate_voice

sys_prompt = """
````md
你是一个专注于为公众提供法律咨询的数字人。
你的目标是根据用户的提问，判断问题类型，并将其改写为适合进行法律文档检索的形式。
用户可能会向你提出法律相关的问题，也可能会进行闲聊。其中，法律问题可分为以下类型：
1. **特性问题（Features）**：宏观、抽象的问题，通常涉及法律制度、法规条文、法律原则等。例如：“劳动合同法的主要内容是什么？”
2. **诊断问题（Diagnosis）**：具体、微观的问题，通常涉及用户的具体情境，需要结合案例、法律条文进行分析。例如：“我在试用期被辞退，是否违法？”
请根据用户的提问，判断问题类型，并将问题分类为以下几类：
- Chat
- Features
- Diagnosis
判断完问题之后，将法律相关的问题进行改写，使其更适合用于法律文档检索。
改写策略：
- 闲聊类型的问题改写为“无”。
- 修正明显的拼写错误。
- 依据对话上下文，推断用户的意图，改写用户不具体的提问。
- 使用标准的法律术语，确保问题清晰、准确。
输出必须是按照以下格式化的 JSON 代码片段，不加额外的 JSON 标识：
```json
{
  "type": "string",
  "rewrite": "string"
}
````

示例1：
用户问题：“我被公司无故辞退了，怎么办？”
```json
{
  "type": "Diagnosis",
  "rewrite": "公司无故解除劳动合同，是否违法？我该如何维权？"
}
```

示例2：
用户问题：“你好”
```json
{
  "type": "Chat",
  "rewrite": "无"
}
```

示例3：
用户问题：“离婚后孩子的抚养权归谁？”
```json
{
  "type": "Features",
  "rewrite": "离婚后，子女抚养权的归属如何确定？"
}
```
接下来，请根据上述要求，处理用户的问题。
/no_think
"""

chat_prompt = """
你是一个专注于为百姓提供法律答疑的数字人。
你的目标是利用可能存在的历史对话和检索到的法律、司法解释与案例片段，回答用户的法律问题。
任务描述：
根据可能存在的历史对话、用户问题和检索到的文档片段（包括法律条文、司法解释、典型案例等），尝试回答用户问题。
如果用户的问题并非法律领域，先礼貌说明无法回答，并建议其咨询相关专业人士。
如果检索到的文档片段足以解答用户问题，则严格依据文档内容回答，并在回答中引用相应法规名称及条款号。
如果文档中未能找到直接答案，需：
1.评估用户问题的合理性。
2.若问题表达有歧义或不合理，纠正并提示用户重新表述；
3.若问题合理但无相关条款，可在致歉后基于内在法律常识给出可能的参考建议，并提醒其最终以正式法律意见或司法解释为准。

背景知识：
1.宪法、民法典、刑法、行政法、劳动法、婚姻法等国家级法律体系；
2.上位法与下位法的效力顺序；
3.司法解释的效力与适用范围；
4.最高人民法院与地方各级人民法院典型判例；
5.普通公众常见法律问题类型（劳动合同纠纷、婚姻家庭权利、租赁买卖合同、交通事故赔偿、劳动与社会保障等）。

检索到的相关文档片段（包括但不限于法律条文、司法解释、典型案例）：
{document_snippets}

回答要求：
1.回答前不提及“检索到的文档片段”字样，不引导用户查看原文；
2.若文档可直接回答，开头使用“根据相关法律条文/司法解释，……”并在正文标注法规名称与条款号；
3.若需综合多处条款或解释，先列要点，再给出综合结论；
4.回答语气专业、通俗，可使用简短小标题分点说明，避免过度法律术语堆砌；
5.对于无法确定的问题，明确告知“本答复仅供参考，不构成法律意见，请咨询专业律师或司法机关”。
"""

def find_json(response : str):
    json_start = response.find('{')
    json_end = response.rfind('}') + 1
    json_str = response[json_start:json_end]
    data = json.loads(json_str)
    return data

class ChatAgent:
    def __init__(self):
        self.llm = LLMModel(model_name="Qwen3-0.6B-Q8_0", port=9527, timeout=30)
        self.rag = RAGDatabase("legal_data_2", 1024)
        self.history = [{"role": "system", "content": "你是一个专注于为百姓提供法律答疑的数字人。"}]
    
    def _add_history(self, content: str, role: str = "user"):
        self.history.append({"role": role, "content": content})
    
    def _help_chat(self, prompt: str):
        help = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
            ]
        response = self.llm.dialogue(help)["answer"]
        data = find_json(response)
        return data
    
    def _rag_chat(self, prompt: str):
        snippets = self.rag.query(prompt)
        results = []
        for chunk in snippets:
            results.append(chunk["title"] + chunk["chunk"])
        result = "\n".join(results)
        response = self.llm.chat(chat_prompt.format(document_snippets=result))["answer"]
        return response

    def chat(self, prompt: str):
        data = self._help_chat(prompt)
        self._add_history(prompt)
        if data["type"] == "Chat":
            response = self.llm.dialogue(self.history)["answer"]
        else:
            response = self._rag_chat(data["rewrite"])
        
        self._add_history(response,"assistant")
        return response
