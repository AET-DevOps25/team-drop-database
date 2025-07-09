#!/usr/bin/env python3
"""
模型切换工具
轻松在OpenAI和本地模型之间切换
"""

import os
from travel_buddy_ai.core.config import settings

def read_env_file():
    """读取.env文件内容"""
    env_path = ".env"
    if not os.path.exists(env_path):
        return {}
    
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # 移除注释
                if '#' in value:
                    value = value.split('#')[0].strip()
                env_vars[key.strip()] = value.strip()
    return env_vars

def write_env_file(env_vars):
    """写入.env文件"""
    env_path = ".env"
    
    # 读取原文件，保留注释和格式
    original_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            original_lines = f.readlines()
    
    # 更新配置
    updated_lines = []
    updated_keys = set()
    
    for line in original_lines:
        line_stripped = line.strip()
        if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
            key = line_stripped.split('=', 1)[0].strip()
            if key in env_vars:
                # 保留注释
                comment = ""
                if '#' in line:
                    comment = " " + line.split('#', 1)[1]
                updated_lines.append(f"{key}={env_vars[key]}{comment}")
                updated_keys.add(key)
            else:
                updated_lines.append(line.rstrip())
        else:
            updated_lines.append(line.rstrip())
    
    # 添加新的配置项
    for key, value in env_vars.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}")
    
    # 写入文件
    with open(env_path, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')

def switch_to_openai():
    """切换到OpenAI模型"""
    env_vars = read_env_file()
    env_vars['LLM_MODEL_TYPE'] = 'openai'
    env_vars['LLM_MODEL_NAME'] = 'gpt-3.5-turbo'
    write_env_file(env_vars)
    print("✅ 已切换到OpenAI模型 (gpt-3.5-turbo)")

def switch_to_ollama(model_name='llama2'):
    """切换到Ollama模型"""
    env_vars = read_env_file()
    env_vars['LLM_MODEL_TYPE'] = 'ollama'
    env_vars['LLM_MODEL_NAME'] = model_name
    write_env_file(env_vars)
    print(f"✅ 已切换到Ollama模型 ({model_name})")

def switch_to_gpt4all(model_name='mistral-7b-openorca.Q4_0.gguf'):
    """切换到GPT4All模型"""
    env_vars = read_env_file()
    env_vars['LLM_MODEL_TYPE'] = 'gpt4all'
    env_vars['LLM_MODEL_NAME'] = model_name
    write_env_file(env_vars)
    print(f"✅ 已切换到GPT4All模型 ({model_name})")

def show_current_config():
    """显示当前配置"""
    env_vars = read_env_file()
    model_type = env_vars.get('LLM_MODEL_TYPE', 'openai')
    model_name = env_vars.get('LLM_MODEL_NAME', 'gpt-3.5-turbo')
    
    print(f"🤖 当前配置:")
    print(f"   模型类型: {model_type}")
    print(f"   模型名称: {model_name}")

def test_current_model():
    """测试当前模型配置"""
    try:
        from travel_buddy_ai.services.qa_system_fixed import AttractionQASystem
        
        print("🧪 测试当前模型配置...")
        qa_system = AttractionQASystem()
        
        model_info = qa_system.get_current_model_info()
        print(f"✅ 模型加载成功: {model_info['model_name']} ({model_info['model_type']})")
        
        # 简单测试
        result = qa_system.ask("你好")
        print(f"✅ 问答测试成功，回答长度: {len(result['answer'])} 字符")
        print(f"   回答预览: {result['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def main():
    """主菜单"""
    while True:
        print("\n🔧 模型切换工具")
        print("=" * 30)
        
        show_current_config()
        
        print("\n选项:")
        print("1. 切换到OpenAI (gpt-3.5-turbo)")
        print("2. 切换到OpenAI (gpt-4)")
        print("3. 切换到Ollama")
        print("4. 切换到GPT4All")
        print("5. 测试当前模型")
        print("6. 显示配置")
        print("0. 退出")
        
        choice = input("\n请选择 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            switch_to_openai()
        elif choice == '2':
            env_vars = read_env_file()
            env_vars['LLM_MODEL_TYPE'] = 'openai'
            env_vars['LLM_MODEL_NAME'] = 'gpt-4'
            write_env_file(env_vars)
            print("✅ 已切换到OpenAI模型 (gpt-4)")
        elif choice == '3':
            model_name = input("输入Ollama模型名称 (默认: llama2): ").strip() or 'llama2'
            switch_to_ollama(model_name)
        elif choice == '4':
            model_name = input("输入GPT4All模型名称 (默认: mistral-7b-openorca.Q4_0.gguf): ").strip() or 'mistral-7b-openorca.Q4_0.gguf'
            switch_to_gpt4all(model_name)
        elif choice == '5':
            test_current_model()
        elif choice == '6':
            show_current_config()
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()
