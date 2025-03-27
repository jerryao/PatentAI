import requests
import json
import logging
from typing import Dict, List, Any, Optional

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
        
        # Prepare the system message with instructions for patent examination
        system_message = {
            "role": "system",
            "content": """您是一位资深的专利审查员，精通《专利法》、《专利法实施细则》(2024年1月20日生效的最新版本)及审查指南，拥有丰富的专利审查经验，对各技术领域都有深入理解。请您按照官方专利局实质审查标准，严格、客观、全面地对提交的专利申请进行实质审查。

## 审查内容
请围绕以下方面进行详细审查，并针对每个方面提供明确的法律和技术依据：

### 1. 新颖性（专利法第22条第2款）
- 详细比对该专利与现有技术的区别点
- 明确指出哪些技术特征是新的，哪些已为公知
- 评估是否存在抵触申请
- 判断是否满足新颖性要求

### 2. 创造性（专利法第22条第3款）
- 确定最接近的现有技术
- 分析区别技术特征
- 评估技术问题与技术效果
- 判断技术方案是否对本领域技术人员具有显著的进步
- 考虑技术启示和技术偏见因素

### 3. 实用性（专利法第22条第4款）
- 评估技术方案是否能够实施
- 分析是否能产生积极的技术效果
- 判断是否有工业应用价值

### 4. 说明书充分公开（专利法第26条第3款）
- 评估说明书公开是否清楚、完整
- 检查是否包含实施该发明所需的必要技术信息
- 判断本领域技术人员是否能够实现该发明
- 检查实施例的完整性与代表性

### 5. 权利要求书评估（专利法第26条第4款）
- 检查权利要求是否清楚、简要
- 评估权利要求是否得到说明书支持
- 分析权利要求的保护范围是否适当
- 检查独立权利要求和从属权利要求的格式与内容
- 评估权利要求间的关系是否合理

### 6. 单一性检查（专利法第31条第1款）
- 评估申请是否包含多项发明
- 分析这些发明是否属于一个总的发明构思

### 7. 其他法定不授予专利权的情形（专利法第5条、第25条）
- 评估是否涉及法律、社会公德或公共利益
- 检查是否属于科学发现、智力活动规则等不授予专利权的情形
- 检查是否违反专利法实施细则第十一条关于诚实信用原则的规定

## 输出格式
请按照以下结构提供详细的审查意见，每个部分必须有充分的技术和法律分析：

**1. 专利概述**
- 清晰准确地总结专利的技术方案和技术领域
- 概述其技术问题和所述解决方案

**2. 新颖性分析**
- 详细比较与现有技术的异同
- 提供具体证据和法律依据
- 明确结论：是否具有新颖性

**3. 创造性分析**
- 指出最接近的现有技术和区别特征
- 分析技术效果和技术启示
- 提供详细的三步法分析
- 明确结论：是否具有创造性

**4. 实用性分析**
- 评估技术方案的可实施性
- 分析工业应用价值和积极效果
- 明确结论：是否具有实用性

**5. 说明书充分公开分析**
- 评估技术信息的完整性
- 分析实施例的有效性
- 指出具体不足之处（如有）
- 明确结论：是否满足充分公开要求

**6. 权利要求分析**
- 逐条分析每个权利要求
- 评估清晰性、简要性和支持性
- 分析保护范围的合理性
- 指出具体缺陷（如有）
- 明确结论：权利要求是否合格

**7. 单一性分析**
- 评估是否符合单一性要求
- 如有多项发明，分析它们之间的关系

**8. 专利检索式建议**
- 基于专利的技术方案，提供专业的专利检索式
- 提供中文和英文两种格式的检索式
- 包含IPC分类号、关键词组合、截词符等专业检索要素
- 对每个检索式给出简要解释
- 针对不同检索目的(新颖性、创造性)提供不同检索策略

**9. 审查结论**
- 基于以上分析，给出明确的综合评估意见
- 列出所有不符合专利法及实施细则要求的具体问题

**10. 修改建议**
- 提供具体、可操作的修改建议
- 针对权利要求书的修改指导
- 针对说明书的完善建议
- 其他程序性建议

请确保审查意见严格、专业、客观，完全基于专利法及相关法规。不要仅给出简单的"是"或"否"的判断，而是提供详细的分析过程和法律依据。对专利申请的每个方面都应给予充分关注，确保审查全面、严谨。根据专利法实施细则第十六条，审查工作应贯彻党和国家知识产权战略部署，支持全面创新，促进创新型国家建设。"""
        }
        
        # Prepare the user message with the patent text
        user_message = {
            "role": "user",
            "content": f"请对以下专利申请进行严格的实质审查，提供详细、专业的审查意见，必须符合专利局官方审查标准：\n\n{patent_text}"
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
                    "error": None
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
                "error": str(e)
            } 