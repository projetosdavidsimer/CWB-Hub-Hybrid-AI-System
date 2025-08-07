#!/usr/bin/env python3
"""
Testes básicos para verificar se o sistema de testes funciona
Melhoria #5 - Testes Automatizados Completos
"""

import pytest
import sys
import os

def test_python_version():
    """Testa se a versão do Python é adequada"""
    assert sys.version_info >= (3, 8), "Python 3.8+ é necessário"

def test_basic_math():
    """Teste básico de matemática"""
    assert 2 + 2 == 4
    assert 10 * 5 == 50
    assert 100 / 4 == 25

def test_string_operations():
    """Teste básico de strings"""
    text = "CWB Hub"
    assert text.upper() == "CWB HUB"
    assert text.lower() == "cwb hub"
    assert len(text) == 7

def test_list_operations():
    """Teste básico de listas"""
    agents = ["Ana", "Carlos", "Sofia", "Gabriel"]
    assert len(agents) == 4
    assert "Ana" in agents
    assert "Pedro" not in agents

def test_dict_operations():
    """Teste básico de dicionários"""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "cwb_hub"
    }
    
    assert config["host"] == "localhost"
    assert config.get("port") == 5432
    assert config.get("timeout", 30) == 30

class TestBasicClass:
    """Classe de teste básica"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.test_data = {"name": "CWB Hub", "version": "1.0"}
    
    def test_setup_data(self):
        """Testa se o setup funcionou"""
        assert self.test_data is not None
        assert self.test_data["name"] == "CWB Hub"
        assert self.test_data["version"] == "1.0"
    
    def test_data_modification(self):
        """Testa modificação de dados"""
        self.test_data["status"] = "active"
        assert self.test_data["status"] == "active"
        assert len(self.test_data) == 3

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
    (5, 10)
])
def test_double_function(input, expected):
    """Teste parametrizado"""
    def double(x):
        return x * 2
    
    assert double(input) == expected

def test_exception_handling():
    """Testa tratamento de exceções"""
    with pytest.raises(ZeroDivisionError):
        result = 10 / 0
    
    with pytest.raises(KeyError):
        data = {"a": 1}
        value = data["b"]

def test_file_system():
    """Testa operações básicas do sistema de arquivos"""
    current_dir = os.getcwd()
    assert os.path.exists(current_dir)
    assert os.path.isdir(current_dir)
    
    # Verificar se estamos no diretório correto
    assert "CWB-Hub-Hybrid-AI-System" in current_dir

@pytest.mark.asyncio
async def test_async_function():
    """Teste de função assíncrona"""
    async def async_add(a, b):
        return a + b
    
    result = await async_add(5, 3)
    assert result == 8

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])