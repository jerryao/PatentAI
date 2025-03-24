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
            "content": """您是一位专业的专利审查员，精通专利法和各领域技术知识。
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

请严格、公正地审查，基于专利法相关规定提供专业意见。"""
        }
        
        # Prepare the user message with the patent text
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