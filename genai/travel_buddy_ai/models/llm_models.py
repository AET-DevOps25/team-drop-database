#!/usr/bin/env python3
"""
LLM Models Module
This module defines the base class for LLM models and specific implementations for OpenAI and Local Ollama.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
from enum import Enum

from travel_buddy_ai.core.config import settings
from travel_buddy_ai.core.logger import get_logger

logger = get_logger(__name__)


class ModelType(Enum):
    """Enumeration for supported LLM model types"""
    OPENAI = "openai"
    LOCAL_OLLAMA = "local_ollama"


class BaseLLMModel(ABC):
    """Base class for LLM models"""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """
        Generate text based on the input prompt
        
        Args:
            prompt: input text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional parameters for the model
            
        Returns:
            Generated text as a string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available for use"""
        pass


class OpenAIModel(BaseLLMModel):
    """OpenAI API model implementation"""
    
    def __init__(self, model_name: str = "gpt-4.1", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info(f"OpenAI Model {model_name} initialized successfully")
        except Exception as e:
            logger.error(f"OpenAI Model initialization failed: {e}")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate text using OpenAI API"""
        if not self.client:
            raise RuntimeError("OpenAI client is not initialized")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional tourism attraction recommendation assistant, capable of providing accurate and useful travel advice based on provided attraction information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response generated successfully, length: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI response generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if OpenAI model is available"""
        return self.client is not None and settings.openai_api_key is not None


class LocalOllamaModel(BaseLLMModel):
    """本地Ollama API模型实现"""
    
    def __init__(self, model_name: str = "llama3.2:3b", api_url: str = "http://ollama.wei-tech.site/api/generate", **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_url = api_url
        self.session = None
        
        try:
            import requests
            self.session = requests.Session()
            # 测试连接
            test_response = self.session.post(
                self.api_url,
                json={
                    "model": model_name,
                    "prompt": "Hello",
                    "stream": False
                },
                timeout=10
            )
            test_response.raise_for_status()
            logger.info(f"Local Ollama model {model_name} at {api_url} initialized successfully")
        except ImportError:
            logger.error("requests library not found, please install: pip install requests")
        except Exception as e:
            logger.warning(f"Local Ollama model connection test failed: {e}, but will continue")
            try:
                import requests
                self.session = requests.Session()
            except ImportError:
                pass
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """使用本地Ollama API生成响应"""
        if not self.session:
            raise RuntimeError("requests session not available")
        
        try:
            # 构建完整的prompt，包含系统提示
            full_prompt = f"""You are a professional tourism attraction recommendation assistant, capable of providing accurate and useful travel advice based on provided attraction information.

User question: {prompt}

Please provide a helpful and detailed response:"""
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            # 添加其他选项
            if kwargs:
                data["options"].update(kwargs)
            
            # 发送请求
            response = self.session.post(
                self.api_url,
                json=data,
                timeout=60  # 本地模型可能需要更长时间
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if 'response' in result:
                answer = result['response'].strip()
            else:
                logger.warning(f"Unexpected response format: {result}")
                answer = str(result)
            
            logger.info(f"Local Ollama response generated successfully, length: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Local Ollama response generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查本地Ollama模型是否可用"""
        if not self.session:
            return False
        
        try:
            # 发送简单测试请求
            response = self.session.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": "test",
                    "stream": False
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class ModelManager:
    """Model manager"""
    
    def __init__(self):
        self.models: Dict[str, BaseLLMModel] = {}
        self.current_model: Optional[BaseLLMModel] = None
        self._load_default_models()
    
    def _load_default_models(self):
        """Load default models"""
        # Try to load OpenAI model
        try:
            openai_model = OpenAIModel()
            if openai_model.is_available():
                self.models["openai"] = openai_model
                if not self.current_model:
                    self.current_model = openai_model
                    logger.info("Set OpenAI as default model")
        except Exception as e:
            logger.warning(f"Failed to load OpenAI model: {e}")
        
        # Try to load Local Ollama model
        try:
            local_ollama_url = getattr(settings, 'local_ollama_url', None)
            local_ollama_model = getattr(settings, 'local_ollama_model', 'llama3.2:3b')
            
            if local_ollama_url:
                local_ollama = LocalOllamaModel(
                    model_name=local_ollama_model,
                    api_url=local_ollama_url
                )
                if local_ollama.is_available():
                    self.models["local_ollama"] = local_ollama
                    if not self.current_model:
                        self.current_model = local_ollama
                        logger.info("Set Local Ollama as default model")
        except Exception as e:
            logger.debug(f"Local Ollama model not available: {e}")
    
    def add_model(self, name: str, model: BaseLLMModel):
        """Add model"""
        self.models[name] = model
        logger.info(f"Added model: {name}")
    
    def set_model(self, name: str) -> bool:
        """Set current model to use"""
        if name in self.models and self.models[name].is_available():
            self.current_model = self.models[name]
            logger.info(f"Switched to model: {name}")
            return True
        else:
            logger.warning(f"Model {name} not available")
            return False
    
    def get_current_model(self) -> Optional[BaseLLMModel]:
        """Get current model"""
        return self.current_model
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return [name for name, model in self.models.items() if model.is_available()]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using current model"""
        if not self.current_model:
            raise RuntimeError("No available model")
        
        return self.current_model.generate(prompt, max_tokens, temperature, **kwargs)


# Global model manager instance
model_manager = ModelManager()
