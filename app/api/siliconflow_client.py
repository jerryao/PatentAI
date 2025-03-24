import requests
import json
import logging
from typing import Dict, List, Any, Optional

# 导入专利检索模块
from app.api.patent_search import PatentSearchClient, compare_patents, extract_patent_keywords

# 设置日志记录器
logger = logging.getLogger(__name__)

class SiliconFlowClient:
    """
    Client for interacting with the SiliconFlow API for patent examination.
    Based on https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions
    """
    
    def __init__(self, api_key: str, api_base: str = "https://api.siliconflow.cn/v1"):
        """
        Initialize the SiliconFlow API client.
        
        Args:
            api_key (str): API key for SiliconFlow API
            api_base (str): Base URL for the API
        """
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        logger.debug(f"SiliconFlow客户端初始化: API基础URL={api_base}")
        
        # 初始化专利检索客户端 - 目前使用模拟数据
        self.patent_search = PatentSearchClient(use_mock=True)
    
    def chat_completions(self, messages: List[Dict[str, str]], 
                        model: str = "deepseek-ai/DeepSeek-R1",
                        temperature: float = 0.7,
                        max_tokens: Optional[int] = None,
                        timeout: int = 180,  # 默认超时时间设置为3分钟
                        **kwargs) -> Dict[str, Any]:
        """
        Call the chat completions API.
        
        Args:
            messages (List[Dict[str, str]]): List of message objects
            model (str): Model to use for the completion
            temperature (float): Temperature parameter for generation
            max_tokens (Optional[int]): Maximum number of tokens to generate
            timeout (int): Request timeout in seconds
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict[str, Any]: API response
        """
        endpoint = f"{self.api_base}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
            
        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value
        
        logger.debug(f"API请求: {endpoint}")
        logger.debug(f"模型: {model}, 温度: {temperature}")
        logger.debug(f"消息数量: {len(messages)}")
        
        try:
            # 设置适当的超时时间
            logger.debug(f"发送API请求，超时设置为{timeout}秒")
            response = requests.post(
                endpoint, 
                headers=self.headers, 
                json=payload,
                timeout=timeout  # 设置请求超时
            )
            # 记录HTTP状态码
            logger.debug(f"API响应状态码: {response.status_code}")
            
            response.raise_for_status()
            json_response = response.json()
            logger.debug("API请求成功完成")
            return json_response
            
        except requests.exceptions.Timeout:
            logger.error(f"API请求超时 (超过{timeout}秒)")
            raise ValueError(f"SiliconFlow API请求超时，请稍后再试")
            
        except requests.exceptions.ConnectionError:
            logger.error("与API服务器的连接错误")
            raise ValueError("无法连接到SiliconFlow API服务器，请检查网络连接")
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else "未知"
            logger.error(f"HTTP错误: {status_code}")
            
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get('error', {}).get('message', str(e))
                    logger.error(f"API错误详情: {error_detail}")
                except:
                    error_detail = e.response.text
                    logger.error(f"API响应文本: {error_detail}")
            
            if status_code == 401:
                raise ValueError("API认证失败，请检查API密钥")
            elif status_code == 429:
                raise ValueError("API请求过于频繁，请稍后再试")
            elif status_code >= 500:
                raise ValueError("API服务器错误，请稍后再试")
            else:
                raise ValueError(f"API请求失败: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            logger.exception(f"API请求异常: {e}")
            raise ValueError(f"API请求失败: {str(e)}")
            
        except Exception as e:
            logger.exception(f"未预期的错误: {e}")
            raise ValueError(f"API请求过程中发生错误: {str(e)}")
    
    def analyze_patent(self, patent_text: str) -> Dict[str, Any]:
        """
        Analyze a patent document using the SiliconFlow API.
        
        Args:
            patent_text (str): Text content of the patent document
            
        Returns:
            Dict[str, Any]: Analysis results including novelty, inventiveness, etc.
        """
        logger.debug("开始专利分析")
        # 裁剪过长的专利文本
        if len(patent_text) > 30000:
            logger.warning(f"专利文本过长({len(patent_text)}字符)，将被截断")
            patent_text = patent_text[:30000] + "...(文本过长，已截断)"
        
        # 1. 首先搜索相关专利
        logger.debug("提取专利关键词进行相关性检索")
        keywords = extract_patent_keywords(patent_text)
        keywords_text = " ".join(keywords[:5])  # 取前5个关键词
        
        logger.debug(f"专利关键词: {keywords_text}")
        similar_patents = self.patent_search.search_patents(keywords_text, limit=5)
        logger.debug(f"找到{len(similar_patents)}个相关专利")
        
        # 2. 分析专利与现有技术的相似性
        patent_comparison = compare_patents(patent_text, similar_patents)
        
        # 3. 构建包含真实参考数据的系统提示
        system_message = {
            "role": "system",
            "content": self._build_system_prompt_with_references(patent_comparison)
        }
        
        # 4. 构建用户消息
        user_message = {
            "role": "user",
            "content": f"请对以下专利申请进行审查，提供实质审查意见：\n\n{patent_text}"
        }
        
        logger.debug("开始调用API")
        try:
            # Call the API with extended timeout for large documents
            response = self.chat_completions(
                messages=[system_message, user_message],
                model="deepseek-ai/DeepSeek-R1",  # Use DeepSeek-R1 model
                temperature=0.2,  # Lower temperature for more focused responses
                max_tokens=4000,   # Adjust based on expected response length
                timeout=300  # 增加超时时间到5分钟，因为专利分析可能需要更长时间
            )
            
            logger.debug("成功获取API响应")
            # Process the response
            try:
                result = {
                    "full_response": response,
                    "examination_result": response["choices"][0]["message"]["content"] if "choices" in response else None,
                    "reasoning_content": response["choices"][0]["message"].get("reasoning_content", None) if "choices" in response else None,
                    "usage": response.get("usage", {}),
                    "error": None,
                    "patent_comparison": patent_comparison  # 添加专利比较结果
                }
                logger.debug("API响应处理成功")
                return result
                
            except Exception as e:
                logger.exception(f"处理API响应时出错: {str(e)}")
                result = {
                    "full_response": response,
                    "examination_result": None,
                    "reasoning_content": None,
                    "usage": response.get("usage", {}),
                    "patent_comparison": patent_comparison,  # 即使API失败，仍然返回专利比较
                    "error": f"处理API响应时出错: {str(e)}"
                }
                return result
                
        except Exception as e:
            logger.exception(f"API调用失败: {str(e)}")
            # 返回错误信息
            return {
                "full_response": None,
                "examination_result": f"专利分析失败，原因: {str(e)}",
                "reasoning_content": None,
                "usage": {},
                "patent_comparison": patent_comparison,  # 即使API失败，仍然返回专利比较
                "error": str(e)
            }
    
    def _build_system_prompt_with_references(self, patent_comparison: Dict[str, Any]) -> str:
        """构建包含参考专利的系统提示"""
        system_prompt = """您是一位专业的专利审查员，精通专利法和各领域技术知识。
请对提交的专利申请进行实质审查，重点评估以下方面：
1. 专利的新颖性 - 是否与现有技术相同
2. 创造性 - 是否对本领域技术人员而言显而易见
3. 实用性 - 是否能够实现并产生积极效果
4. 充分公开 - 说明书是否清楚、完整地公开了发明
5. 权利要求书 - 是否清楚、简要，是否得到说明书支持

请按以下格式提供审查意见：
- 专利概述：对专利技术方案的简要总结
- 新颖性分析：评估是否具有新颖性
- 创造性分析：评估是否具有创造性
- 实用性分析：评估是否具有实用性
- 充分公开分析：评估说明书是否充分公开
- 权利要求分析：评估权利要求是否清楚、简要，是否得到说明书支持
- 审查结论：给出综合评估意见
- 修改建议：对权利要求书、说明书等提出具体修改建议

以下是通过专利数据库检索到的相关现有技术参考，请在审查过程中详细参考这些信息，特别是在新颖性和创造性分析中：
"""

        # 添加关键词信息
        keywords = patent_comparison.get("keywords", [])
        if keywords:
            system_prompt += f"\n【检索关键词】: {', '.join(keywords)}\n"
        
        # 添加现有技术参考
        similar_patents = patent_comparison.get("similar_patents", [])
        if similar_patents:
            system_prompt += "\n【相关现有技术文献】:\n"
            for i, patent in enumerate(similar_patents, 1):
                # 提取专利信息
                title = patent.get("title", "无标题")
                pub_num = patent.get("publication_number", "无公开号")
                pub_date = patent.get("publication_date", "无公开日期")
                assignee = patent.get("assignee", "无申请人")
                abstract = patent.get("abstract", "无摘要")
                
                # 获取相似度分析（如果有）
                similarity_details = None
                for detail in patent_comparison.get("novelty_analysis", {}).get("details", []):
                    if detail.get("patent_number") == pub_num:
                        similarity_details = detail
                        break
                
                system_prompt += f"\n{i}. 【专利】: {title} ({pub_num})\n"
                system_prompt += f"   【公开日期】: {pub_date}\n"
                system_prompt += f"   【申请人】: {assignee}\n"
                system_prompt += f"   【摘要】: {abstract}\n"
                
                if similarity_details:
                    system_prompt += f"   【相似度评估】: {similarity_details.get('similarity_comment', '')}\n"
                    overlap_keywords = similarity_details.get("overlap_keywords", [])
                    if overlap_keywords:
                        system_prompt += f"   【重叠关键词】: {', '.join(overlap_keywords)}\n"
        
        # 添加新颖性总体评分
        novelty_score = patent_comparison.get("novelty_analysis", {}).get("score")
        if novelty_score is not None:
            system_prompt += f"\n【新颖性初步评分】: {novelty_score}/10 (自动评估，仅供参考)\n"
        
        system_prompt += """
【重要提示】：
1. 请基于以上现有技术参考进行分析，而不是依赖您的模型知识中可能已过时或不准确的信息
2. 请严格按照专利法的标准评估新颖性和创造性，给出客观专业的审查意见
3. 在引用上述现有技术文献时，请清晰标注文献编号
4. 如果专利申请确实具有新颖性和创造性，请明确指出与现有技术的区别

请严格、公正地审查，基于专利法相关规定提供专业意见。"""

        return system_prompt 