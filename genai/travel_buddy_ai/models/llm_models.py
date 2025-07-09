#!/usr/bin/env python3
"""
LLM模型管理系统
支持云端模型（OpenAI）和本地模型（GPT4All, LLaMA等）
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from enum import Enum

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class ModelType(Enum):
    """模型类型枚举"""
    OPENAI = "openai"
    GPT4ALL = "gpt4all"
    LLAMACPP = "llamacpp"
    OLLAMA = "ollama"


class BaseLLMModel(ABC):
    """LLM模型基类"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """
        生成回答
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用"""
        pass


class OpenAIModel(BaseLLMModel):
    """OpenAI模型实现"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info(f"OpenAI模型 {model_name} 初始化成功")
        except Exception as e:
            logger.error(f"OpenAI模型初始化失败: {e}")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用OpenAI API生成回答"""
        if not self.client:
            raise RuntimeError("OpenAI客户端未初始化")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的旅游景点推荐助手，能够基于提供的景点信息为用户提供准确、有用的旅游建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI生成回答成功，长度: {len(answer)} 字符")
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI生成回答失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查OpenAI模型是否可用"""
        return self.client is not None and settings.openai_api_key is not None


class GPT4AllModel(BaseLLMModel):
    """GPT4All本地模型实现"""
    
    def __init__(self, model_name: str = "mistral-7b-openorca.Q4_0.gguf", **kwargs):
        super().__init__(model_name, **kwargs)
        self.model = None
        try:
            import gpt4all
            # 可以指定模型路径
            model_path = kwargs.get('model_path', None)
            if model_path and os.path.exists(model_path):
                self.model = gpt4all.GPT4All(model_path)
            else:
                self.model = gpt4all.GPT4All(model_name)
            logger.info(f"GPT4All模型 {model_name} 初始化成功")
        except ImportError:
            logger.warning("GPT4All未安装，请运行: pip install gpt4all")
        except Exception as e:
            logger.error(f"GPT4All模型初始化失败: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用GPT4All生成回答"""
        if not self.model:
            raise RuntimeError("GPT4All模型未初始化")
        
        try:
            # GPT4All的参数名称可能不同
            response = self.model.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                **kwargs
            )
            
            logger.info(f"GPT4All生成回答成功，长度: {len(response)} 字符")
            return response.strip()
            
        except Exception as e:
            logger.error(f"GPT4All生成回答失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查GPT4All模型是否可用"""
        return self.model is not None


class LlamaCppModel(BaseLLMModel):
    """llama-cpp-python本地模型实现"""
    
    def __init__(self, model_name: str, model_path: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.model = None
        try:
            from llama_cpp import Llama
            
            # 默认参数
            default_kwargs = {
                'n_ctx': 2048,  # 上下文长度
                'n_batch': 512,  # 批处理大小
                'verbose': False,
            }
            default_kwargs.update(kwargs)
            
            self.model = Llama(model_path=model_path, **default_kwargs)
            logger.info(f"LlamaCpp模型 {model_name} 初始化成功")
        except ImportError:
            logger.warning("llama-cpp-python未安装，请运行: pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"LlamaCpp模型初始化失败: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用LlamaCpp生成回答"""
        if not self.model:
            raise RuntimeError("LlamaCpp模型未初始化")
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["Human:", "Assistant:", "\n\n"],
                **kwargs
            )
            
            answer = response['choices'][0]['text'].strip()
            logger.info(f"LlamaCpp生成回答成功，长度: {len(answer)} 字符")
            return answer
            
        except Exception as e:
            logger.error(f"LlamaCpp生成回答失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查LlamaCpp模型是否可用"""
        return self.model is not None


class OllamaModel(BaseLLMModel):
    """Ollama本地模型实现"""
    
    def __init__(self, model_name: str = "llama2", **kwargs):
        super().__init__(model_name, **kwargs)
        self.client = None
        try:
            import ollama
            self.client = ollama.Client()
            # 测试连接
            self.client.list()
            logger.info(f"Ollama模型 {model_name} 初始化成功")
        except ImportError:
            logger.warning("Ollama未安装，请运行: pip install ollama")
        except Exception as e:
            logger.error(f"Ollama模型初始化失败: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用Ollama生成回答"""
        if not self.client:
            raise RuntimeError("Ollama客户端未初始化")
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': temperature,
                    **kwargs
                }
            )
            
            answer = response['response'].strip()
            logger.info(f"Ollama生成回答成功，长度: {len(answer)} 字符")
            return answer
            
        except Exception as e:
            logger.error(f"Ollama生成回答失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查Ollama模型是否可用"""
        try:
            if self.client:
                self.client.list()
                return True
        except:
            pass
        return False


class ModelManager:
    """模型管理器"""
    
    def __init__(self):
        self.models: Dict[str, BaseLLMModel] = {}
        self.current_model: Optional[BaseLLMModel] = None
        self._load_default_models()
    
    def _load_default_models(self):
        """加载默认模型"""
        # 尝试加载OpenAI模型
        try:
            openai_model = OpenAIModel()
            if openai_model.is_available():
                self.models["openai"] = openai_model
                if not self.current_model:
                    self.current_model = openai_model
                    logger.info("设置OpenAI为默认模型")
        except Exception as e:
            logger.warning(f"加载OpenAI模型失败: {e}")
        
        # 尝试加载本地模型（如果配置了的话）
        self._try_load_local_models()
    
    def _try_load_local_models(self):
        """尝试加载本地模型"""
        # GPT4All
        try:
            gpt4all_model = GPT4AllModel()
            if gpt4all_model.is_available():
                self.models["gpt4all"] = gpt4all_model
                if not self.current_model:
                    self.current_model = gpt4all_model
                    logger.info("设置GPT4All为默认模型")
        except Exception as e:
            logger.debug(f"GPT4All模型不可用: {e}")
        
        # Ollama
        try:
            # 从配置文件读取模型名称
            ollama_model_name = getattr(settings, 'llm_model_name', 'llama2')
            ollama_model = OllamaModel(model_name=ollama_model_name)
            if ollama_model.is_available():
                self.models["ollama"] = ollama_model
                if not self.current_model:
                    self.current_model = ollama_model
                    logger.info("设置Ollama为默认模型")
        except Exception as e:
            logger.debug(f"Ollama模型不可用: {e}")
    
    def add_model(self, name: str, model: BaseLLMModel):
        """添加模型"""
        self.models[name] = model
        logger.info(f"添加模型: {name}")
    
    def set_model(self, name: str) -> bool:
        """设置当前使用的模型"""
        if name in self.models and self.models[name].is_available():
            self.current_model = self.models[name]
            logger.info(f"切换到模型: {name}")
            return True
        else:
            logger.warning(f"模型 {name} 不可用")
            return False
    
    def get_current_model(self) -> Optional[BaseLLMModel]:
        """获取当前模型"""
        return self.current_model
    
    def list_available_models(self) -> List[str]:
        """列出可用的模型"""
        return [name for name, model in self.models.items() if model.is_available()]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用当前模型生成回答"""
        if not self.current_model:
            raise RuntimeError("没有可用的模型")
        
        return self.current_model.generate(prompt, max_tokens, temperature, **kwargs)


# 全局模型管理器实例
model_manager = ModelManager()
