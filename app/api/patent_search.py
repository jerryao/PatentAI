import os
import json
import logging
import random
import re
from typing import List, Dict, Any, Optional
from collections import Counter

# 设置日志记录器
logger = logging.getLogger(__name__)

class PatentSearchClient:
    """
    用于专利检索的客户端
    支持真实API检索和模拟数据
    """
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, use_mock: bool = True):
        """
        初始化专利检索客户端
        
        Args:
            api_key: API密钥，如果未指定则从环境变量获取
            api_base: API基础URL，如果未指定则从环境变量获取
            use_mock: 是否使用模拟数据
        """
        self.use_mock = use_mock
        
        if not use_mock:
            self.api_key = api_key or os.environ.get("PATENT_API_KEY")
            self.api_base = api_base or os.environ.get("PATENT_API_BASE", "https://api.patentsearch.com/v1")
            if not self.api_key:
                logger.warning("未设置专利API密钥，将使用模拟数据")
                self.use_mock = True
        
        logger.debug(f"专利检索客户端初始化完成，使用模拟数据: {self.use_mock}")
    
    def search_patents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关专利
        
        Args:
            query: 搜索查询词
            limit: 返回结果数量上限
            
        Returns:
            List[Dict]: 专利列表
        """
        logger.debug(f"专利检索: 查询={query}, 限制={limit}")
        
        if self.use_mock:
            logger.debug("使用模拟数据进行专利检索")
            return self._generate_mock_patents(query, limit)
        
        # 真实API实现（待完成）
        logger.warning("真实API检索功能尚未实现，使用模拟数据")
        return self._generate_mock_patents(query, limit)
    
    def _generate_mock_patents(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """生成模拟专利数据，基于查询关键词"""
        logger.debug("生成模拟专利数据")
        
        # 分析查询词，确定相关领域
        query_lower = query.lower()
        
        # 技术领域映射
        tech_areas = {
            "blockchain": self._generate_blockchain_patents,
            "区块链": self._generate_blockchain_patents,
            "artificial intelligence": self._generate_ai_patents,
            "ai": self._generate_ai_patents,
            "人工智能": self._generate_ai_patents,
            "machine learning": self._generate_ai_patents,
            "机器学习": self._generate_ai_patents,
            "internet of things": self._generate_iot_patents,
            "iot": self._generate_iot_patents,
            "物联网": self._generate_iot_patents
        }
        
        # 选择合适的生成器
        generator = None
        for key, gen_func in tech_areas.items():
            if key in query_lower:
                generator = gen_func
                break
        
        # 如果没有匹配的领域，使用通用生成器
        if not generator:
            generator = self._generate_generic_patents
        
        # 生成结果
        patents = generator(limit)
        
        # 确保唯一性
        unique_patents = []
        seen_numbers = set()
        
        for patent in patents:
            if patent["publication_number"] not in seen_numbers:
                seen_numbers.add(patent["publication_number"])
                unique_patents.append(patent)
                if len(unique_patents) >= limit:
                    break
        
        # 如果数量不足，补充通用专利
        if len(unique_patents) < limit:
            generic_patents = self._generate_generic_patents(limit - len(unique_patents))
            for patent in generic_patents:
                if patent["publication_number"] not in seen_numbers:
                    seen_numbers.add(patent["publication_number"])
                    unique_patents.append(patent)
                    if len(unique_patents) >= limit:
                        break
        
        logger.debug(f"已生成{len(unique_patents)}条模拟专利数据")
        return unique_patents
    
    def _generate_blockchain_patents(self, count: int) -> List[Dict[str, Any]]:
        """生成区块链领域的模拟专利"""
        templates = [
            {
                "title": "一种基于区块链的分布式存储方法及系统",
                "abstract": "本专利提出一种基于区块链技术的分布式存储方法，通过智能合约实现数据的安全存储和高效访问，解决了传统中心化存储系统的单点故障问题，并提高了数据的可靠性和完整性。",
                "assignee": "链信科技有限公司",
                "publication_date": "2023-08-15"
            },
            {
                "title": "区块链驱动的去中心化身份认证系统",
                "abstract": "本发明公开了一种区块链驱动的去中心化身份认证系统，采用多签名技术和零知识证明，在保护用户隐私的同时实现了可靠的身份验证，适用于金融服务、政务系统等多种场景。",
                "assignee": "未来区块科技集团",
                "publication_date": "2022-11-27"
            },
            {
                "title": "基于区块链的供应链溯源方法",
                "abstract": "本专利提出一种基于区块链的供应链溯源方法，通过分布式账本记录产品从生产到销售的全过程信息，确保数据不可篡改，解决了传统溯源系统中的信任问题，提高了产品质量追溯的透明度。",
                "assignee": "溯源链科技股份有限公司",
                "publication_date": "2023-01-05"
            },
            {
                "title": "区块链跨链通信协议及实现方法",
                "abstract": "本发明涉及一种区块链跨链通信协议及其实现方法，通过设计跨链消息格式和验证机制，实现了不同区块链网络之间的安全可靠通信，提高了区块链生态系统的互操作性。",
                "assignee": "跨链技术研究院",
                "publication_date": "2022-07-19"
            },
            {
                "title": "一种基于区块链的数字资产交易系统",
                "abstract": "本专利公开了一种基于区块链技术的数字资产交易系统，采用智能合约自动执行交易，确保交易的安全性和不可篡改性，同时通过分布式账本技术降低了交易成本，提高了效率。",
                "assignee": "数字资产交易集团",
                "publication_date": "2023-03-28"
            },
            {
                "title": "区块链共识算法优化方法",
                "abstract": "本发明提出一种区块链共识算法的优化方法，通过改进拜占庭容错机制，降低了计算资源消耗，提高了交易处理速度，同时保持了系统的安全性和去中心化特性。",
                "assignee": "区块链技术研究所",
                "publication_date": "2022-09-12"
            }
        ]
        
        return self._generate_from_templates(templates, count, "CN10", "区块链")
    
    def _generate_ai_patents(self, count: int) -> List[Dict[str, Any]]:
        """生成人工智能领域的模拟专利"""
        templates = [
            {
                "title": "基于深度学习的自然语言处理方法",
                "abstract": "本发明提出一种基于深度学习的自然语言处理方法，利用改进的Transformer模型结构，显著提高了文本理解和生成的准确性，在机器翻译、内容摘要和情感分析等任务上取得了突破性进展。",
                "assignee": "智能语言科技公司",
                "publication_date": "2023-05-22"
            },
            {
                "title": "一种多模态人工智能推理系统",
                "abstract": "本专利公开了一种多模态人工智能推理系统，能够同时处理图像、文本和声音数据，通过跨模态特征融合技术实现了更准确的内容理解和判断，适用于智能助手、内容审核等场景。",
                "assignee": "融合智能科技有限公司",
                "publication_date": "2022-12-10"
            },
            {
                "title": "神经网络模型压缩方法及装置",
                "abstract": "本发明涉及一种神经网络模型压缩方法及装置，通过知识蒸馏和量化技术，大幅减小了模型体积，降低了计算资源需求，使深度学习模型能够在资源受限的移动设备上高效运行。",
                "assignee": "轻量智能技术公司",
                "publication_date": "2023-02-18"
            },
            {
                "title": "自适应强化学习算法及其应用",
                "abstract": "本专利提出一种自适应强化学习算法，能够根据环境变化动态调整学习策略，显著提高了智能体在复杂环境中的决策能力和适应能力，特别适用于自动驾驶和机器人控制领域。",
                "assignee": "自动驾驶技术研究院",
                "publication_date": "2022-08-05"
            },
            {
                "title": "分布式联邦学习系统及方法",
                "abstract": "本发明公开了一种分布式联邦学习系统及方法，通过保护数据隐私的方式实现多方数据协同训练，解决了数据孤岛问题，同时保证了模型性能，适用于医疗、金融等敏感数据领域。",
                "assignee": "隐私计算技术公司",
                "publication_date": "2023-04-07"
            }
        ]
        
        return self._generate_from_templates(templates, count, "CN20", "人工智能")
    
    def _generate_iot_patents(self, count: int) -> List[Dict[str, Any]]:
        """生成物联网领域的模拟专利"""
        templates = [
            {
                "title": "一种低功耗物联网通信协议",
                "abstract": "本发明提出一种低功耗物联网通信协议，通过优化数据包结构和传输机制，大幅降低了设备能耗，延长了电池寿命，同时保持了通信的可靠性，适用于大规模物联网部署场景。",
                "assignee": "物联通信科技有限公司",
                "publication_date": "2023-06-14"
            },
            {
                "title": "智能家居设备互联系统及控制方法",
                "abstract": "本专利公开了一种智能家居设备互联系统及控制方法，通过统一的通信标准和控制协议，实现了不同厂商、不同类型设备的无缝连接和协同工作，提升了用户的智能家居体验。",
                "assignee": "智家科技集团",
                "publication_date": "2022-10-30"
            },
            {
                "title": "基于边缘计算的物联网数据处理方法",
                "abstract": "本发明涉及一种基于边缘计算的物联网数据处理方法，将部分计算任务从云端迁移到边缘设备，降低了网络延迟，减轻了云服务器负担，同时提高了数据处理实时性和隐私保护能力。",
                "assignee": "边缘计算技术公司",
                "publication_date": "2023-01-25"
            },
            {
                "title": "物联网设备安全认证系统",
                "abstract": "本专利提出一种物联网设备安全认证系统，采用轻量级加密算法和设备唯一标识技术，有效防止了设备仿冒和非法接入，提高了物联网系统的整体安全性，适用于智慧城市、工业物联网等场景。",
                "assignee": "安全物联技术有限公司",
                "publication_date": "2022-07-08"
            }
        ]
        
        return self._generate_from_templates(templates, count, "CN30", "物联网")
    
    def _generate_generic_patents(self, count: int) -> List[Dict[str, Any]]:
        """生成通用技术领域的模拟专利"""
        templates = [
            {
                "title": "一种智能电子设备散热结构",
                "abstract": "本发明公开了一种智能电子设备散热结构，通过优化散热通道设计和材料选用，显著提高了散热效率，降低了设备温度，延长了电子元件寿命，同时减小了噪音，适用于各类高性能电子设备。",
                "assignee": "智能硬件技术公司",
                "publication_date": "2023-03-12"
            },
            {
                "title": "可降解环保包装材料及其制备方法",
                "abstract": "本专利提出一种可降解环保包装材料及其制备方法，采用天然植物纤维和生物基聚合物，具有良好的机械强度和防水性能，同时在自然环境中可完全降解，减少了环境污染。",
                "assignee": "绿色包装材料有限公司",
                "publication_date": "2022-09-05"
            },
            {
                "title": "高效太阳能电池及其制造工艺",
                "abstract": "本发明涉及一种高效太阳能电池及其制造工艺，通过改进电池结构和制造工艺，显著提高了光电转换效率，降低了制造成本，具有良好的耐候性和可靠性，推动了可再生能源的应用。",
                "assignee": "新能源科技研究院",
                "publication_date": "2023-02-28"
            },
            {
                "title": "智能交通信号控制系统",
                "abstract": "本专利公开了一种智能交通信号控制系统，根据实时交通流量数据动态调整信号灯配时，优化了交通流量分配，减少了交通拥堵，提高了道路通行效率，适用于城市交通管理。",
                "assignee": "智慧交通控制技术公司",
                "publication_date": "2022-11-15"
            },
            {
                "title": "新型医用抗菌材料及应用",
                "abstract": "本发明提出一种新型医用抗菌材料及其应用，通过纳米材料表面修饰技术，赋予材料持久稳定的抗菌性能，同时保持良好的生物相容性，可用于医疗器械、伤口敷料等多种医疗产品。",
                "assignee": "医疗材料研究所",
                "publication_date": "2023-05-10"
            }
        ]
        
        return self._generate_from_templates(templates, count, "CN40", "通用技术")
    
    def _generate_from_templates(self, templates: List[Dict[str, Any]], count: int, prefix: str, domain: str) -> List[Dict[str, Any]]:
        """从模板生成专利数据"""
        patents = []
        
        for i in range(count):
            # 随机选择一个模板
            template = random.choice(templates)
            
            # 生成唯一的专利号
            unique_id = random.randint(1000000, 9999999)
            publication_number = f"{prefix}{unique_id}A1"
            
            # 复制模板并添加唯一标识
            patent = template.copy()
            patent["publication_number"] = publication_number
            patent["domain"] = domain
            
            # 添加IPC分类
            patent["ipc_class"] = self._generate_ipc_class(domain)
            
            patents.append(patent)
        
        return patents
    
    def _generate_ipc_class(self, domain: str) -> str:
        """根据领域生成IPC分类号"""
        ipc_classes = {
            "区块链": ["G06Q 20/00", "H04L 9/00", "G06F 16/00"],
            "人工智能": ["G06N 3/00", "G06N 20/00", "G06K 9/00"],
            "物联网": ["H04W 4/00", "H04L 29/00", "G08C 17/00"],
            "通用技术": ["G06F 1/00", "H01L 21/00", "B65D 65/00"]
        }
        
        if domain in ipc_classes:
            return random.choice(ipc_classes[domain])
        return "G06F 1/00"  # 默认分类


def extract_patent_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    从专利文本中提取关键词
    
    Args:
        text: 专利文本
        max_keywords: 最大关键词数量
        
    Returns:
        List[str]: 关键词列表
    """
    logger.debug(f"从文本中提取关键词，最大数量: {max_keywords}")
    
    # 移除常见标点符号和特殊字符
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 分词并转换为小写
    words = text.lower().split()
    
    # 移除停用词（简化版，实际应使用完整停用词表）
    stopwords = {
        "的", "了", "和", "与", "或", "是", "在", "有", "为", "以", "该", "所", "一种", "本发明", "所述",
        "the", "a", "an", "and", "or", "is", "in", "to", "for", "with", "by", "on", "of", "that", "this"
    }
    
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    
    # 统计词频
    word_counts = Counter(filtered_words)
    
    # 提取前N个最频繁的词作为关键词
    keywords = [word for word, _ in word_counts.most_common(max_keywords)]
    
    logger.debug(f"提取到的关键词: {keywords}")
    return keywords


def compare_patents(patent_text: str, similar_patents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    比较专利文本与相似专利的关系，评估新颖性
    
    Args:
        patent_text: 待分析的专利文本
        similar_patents: 相似专利列表
        
    Returns:
        Dict: 比较结果，包含新颖性分析
    """
    logger.debug(f"开始比较专利文本与{len(similar_patents)}个相似专利")
    
    # 提取专利文本的关键词
    patent_keywords = set(extract_patent_keywords(patent_text, 20))
    
    # 初始化结果
    result = {
        "keywords": list(patent_keywords),
        "similar_patents": similar_patents,
        "novelty_analysis": {
            "score": 0,
            "summary": "",
            "details": []
        }
    }
    
    # 如果没有找到相似专利，返回最高新颖性评分
    if not similar_patents:
        result["novelty_analysis"]["score"] = 9
        result["novelty_analysis"]["summary"] = "未找到相关专利，该专利技术可能具有高度新颖性。"
        return result
    
    # 计算与每个相似专利的相似度
    similarity_details = []
    total_similarity = 0
    
    for patent in similar_patents:
        # 提取专利摘要的关键词
        abstract_keywords = set(extract_patent_keywords(patent.get("abstract", ""), 15))
        
        # 计算关键词重叠
        overlap_keywords = patent_keywords.intersection(abstract_keywords)
        overlap_count = len(overlap_keywords)
        
        # 计算相似度得分 (0.0-1.0)
        similarity_score = min(1.0, overlap_count / max(1, len(patent_keywords) * 0.5))
        total_similarity += similarity_score
        
        # 生成相似度评论
        if similarity_score > 0.7:
            comment = "高度相似，可能存在新颖性问题。"
        elif similarity_score > 0.4:
            comment = "部分相似，建议进一步区分技术特征。"
        else:
            comment = "相似度较低，技术方案存在明显差异。"
        
        # 添加详细分析
        similarity_details.append({
            "patent_number": patent.get("publication_number"),
            "similarity_score": similarity_score,
            "overlap_count": overlap_count,
            "overlap_keywords": list(overlap_keywords),
            "similarity_comment": comment
        })
    
    # 排序详细分析，高相似度优先
    similarity_details = sorted(similarity_details, key=lambda x: x["similarity_score"], reverse=True)
    
    # 计算平均相似度
    avg_similarity = total_similarity / len(similar_patents) if similar_patents else 0
    
    # 根据平均相似度确定新颖性评分 (10分制，越高越新颖)
    novelty_score = int(10 - min(9, avg_similarity * 10))
    
    # 生成新颖性总结
    if novelty_score >= 7:
        summary = "该专利与现有技术相比具有较高的新颖性。"
    elif novelty_score >= 4:
        summary = "该专利与现有技术有一定重叠，需要突出差异化特征。"
    else:
        summary = "该专利与现有技术高度相似，新颖性存在显著问题。"
    
    # 更新结果
    result["novelty_analysis"]["score"] = novelty_score
    result["novelty_analysis"]["summary"] = summary
    result["novelty_analysis"]["details"] = similarity_details
    
    logger.debug(f"专利比较完成，新颖性评分: {novelty_score}/10")
    return result 