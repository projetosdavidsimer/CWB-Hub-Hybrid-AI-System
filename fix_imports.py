#!/usr/bin/env python3
"""
Script para corrigir importações relativas no CWB Hub
"""

import os
import re

def fix_imports_in_file(file_path):
    """Corrige importações em um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrões de importação a corrigir
        patterns = [
            (r'from \.\.core\.hybrid_ai_orchestrator import', 
             '''try:
    from ..core.hybrid_ai_orchestrator import'''),
            (r'from \.\.agents\.base_agent import',
             '''try:
    from ..agents.base_agent import'''),
            (r'from \.\.communication\.collaboration_framework import',
             '''try:
    from ..communication.collaboration_framework import'''),
            (r'from \.\.utils\.requirement_analyzer import',
             '''try:
    from ..utils.requirement_analyzer import'''),
            (r'from \.\.utils\.response_synthesizer import',
             '''try:
    from ..utils.response_synthesizer import''')
        ]
        
        # Aplicar correções
        modified = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                # Adicionar fallback para importação absoluta
                content = re.sub(
                    pattern + r'([^\n]+)',
                    replacement + r'\1\nexcept ImportError:\n    from ' + 
                    pattern.replace(r'from \.\.', '').replace(r'\.', '/').replace('/', '.') + r'\1',
                    content
                )
                modified = True
        
        # Salvar se modificado
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigido: {file_path}")
        else:
            print(f"ℹ️ Sem alterações: {file_path}")
            
    except Exception as e:
        print(f"❌ Erro em {file_path}: {e}")

def main():
    """Função principal"""
    print("🔧 Corrigindo importações do CWB Hub...")
    
    # Arquivos a corrigir
    files_to_fix = [
        'src/core/hybrid_ai_orchestrator.py',
        'src/communication/collaboration_framework.py',
        'src/utils/requirement_analyzer.py',
        'src/utils/response_synthesizer.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_imports_in_file(file_path)
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print("✅ Correção de importações concluída!")

if __name__ == "__main__":
    main()