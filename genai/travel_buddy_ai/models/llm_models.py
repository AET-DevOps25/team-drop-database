#!/usr/bin/env python3
"""
LLM Models Module
This module defines the base class for LLM models and specific implementations for OpenAI, GPT4All, LlamaCpp, and Ollama.
It also includes a model manager to handle different models and their configurations.
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
    GPT4ALL = "gpt4all"
    LLAMACPP = "llamacpp"
    OLLAMA = "ollama"


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
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", **kwargs):
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


class GPT4AllModel(BaseLLMModel):
    """GPT4All local model implementation"""
    
    def __init__(self, model_name: str = "mistral-7b-openorca.Q4_0.gguf", **kwargs):
        super().__init__(model_name, **kwargs)
        self.model = None
        try:
            import gpt4all
            # Can specify model path
            model_path = kwargs.get('model_path', None)
            if model_path and os.path.exists(model_path):
                self.model = gpt4all.GPT4All(model_path)
            else:
                self.model = gpt4all.GPT4All(model_name)
            logger.info(f"GPT4All model {model_name} initialized successfully")
        except ImportError:
            logger.warning("GPT4All not installed, please run: pip install gpt4all")
        except Exception as e:
            logger.error(f"GPT4All model initialization failed: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using GPT4All"""
        if not self.model:
            raise RuntimeError("GPT4All model not initialized")
        
        try:
            # GPT4All parameter names may be different
            response = self.model.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                **kwargs
            )
            
            logger.info(f"GPT4All response generated successfully, length: {len(response)} characters")
            return response.strip()
            
        except Exception as e:
            logger.error(f"GPT4All response generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if GPT4All model is available"""
        return self.model is not None


class LlamaCppModel(BaseLLMModel):
    """llama-cpp-python local model implementation"""
    
    def __init__(self, model_name: str, model_path: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.model = None
        try:
            from llama_cpp import Llama
            
            # Default parameters
            default_kwargs = {
                'n_ctx': 2048,  # Context length
                'n_batch': 512,  # Batch size
                'verbose': False,
            }
            default_kwargs.update(kwargs)
            
            self.model = Llama(model_path=model_path, **default_kwargs)
            logger.info(f"LlamaCpp model {model_name} initialized successfully")
        except ImportError:
            logger.warning("llama-cpp-python not installed, please run: pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"LlamaCpp model initialization failed: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using LlamaCpp"""
        if not self.model:
            raise RuntimeError("LlamaCpp model not initialized")
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["Human:", "Assistant:", "\n\n"],
                **kwargs
            )
            
            answer = response['choices'][0]['text'].strip()
            logger.info(f"LlamaCpp response generated successfully, length: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"LlamaCpp response generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if LlamaCpp model is available"""
        return self.model is not None


class OllamaModel(BaseLLMModel):
    """Ollama local model implementation"""
    
    def __init__(self, model_name: str = "llama2", **kwargs):
        super().__init__(model_name, **kwargs)
        self.client = None
        try:
            import ollama
            self.client = ollama.Client()
            # Test connection
            self.client.list()
            logger.info(f"Ollama model {model_name} initialized successfully")
        except ImportError:
            logger.warning("Ollama not installed, please run: pip install ollama")
        except Exception as e:
            logger.error(f"Ollama model initialization failed: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> str:
        """Generate response using Ollama"""
        if not self.client:
            raise RuntimeError("Ollama client not initialized")
        
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
            logger.info(f"Ollama response generated successfully, length: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Ollama response generation failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama model is available"""
        try:
            if self.client:
                self.client.list()
                return True
        except:
            pass
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
        
        # Try to load local models (if configured)
        self._try_load_local_models()
    
    def _try_load_local_models(self):
        """Try to load local models"""
        # GPT4All
        try:
            gpt4all_model = GPT4AllModel()
            if gpt4all_model.is_available():
                self.models["gpt4all"] = gpt4all_model
                if not self.current_model:
                    self.current_model = gpt4all_model
                    logger.info("Set GPT4All as default model")
        except Exception as e:
            logger.debug(f"GPT4All model not available: {e}")
        
        # Ollama
        try:
            # Read model name from config file
            ollama_model_name = getattr(settings, 'llm_model_name', 'llama2')
            ollama_model = OllamaModel(model_name=ollama_model_name)
            if ollama_model.is_available():
                self.models["ollama"] = ollama_model
                if not self.current_model:
                    self.current_model = ollama_model
                    logger.info("Set Ollama as default model")
        except Exception as e:
            logger.debug(f"Ollama model not available: {e}")
    
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
