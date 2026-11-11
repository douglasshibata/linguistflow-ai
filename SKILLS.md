# SKILLS.md - LinguistFlow AI

Diretrizes para evolução do tutor de idiomas adaptativo.

## 🛡️ Auditoria de Segurança

1. **Privacidade de Áudio:** Garanta que gravações de voz dos usuários sejam processadas de forma efêmera ou anonimizada.
2. **Sanitização de Grafo:** Valide inputs que alteram o Grafo de Conhecimento no Neo4j para evitar corrupção de dados educacionais.
3. **Filtro de Conteúdo:** O LLM gerador de lições deve possuir filtros para evitar conteúdo inapropriado ou ofensivo.

## 📈 Melhorias Sugeridas

1. **Inteligência Educacional:**
   - Implementar o algoritmo de Repetição Espaçada (Anki/SuperMemo) de forma nativa integrada ao MongoDB.
   - Refinar a análise de fonemas para suportar sotaques regionais específicos.
2. **Gamificação:**
   - Criar missões dinâmicas baseadas em nós não explorados no Grafo de Conhecimento.
3. **Performance:**
   - Otimizar o tempo de resposta do Whisper usando `faster-whisper` ou inferência via TensorRT.

## 🤖 Papel do Claude

- **Linguista Computacional:** Ajude a estruturar a taxonomia de idiomas no Neo4j.
- **Engenheiro de ML:** Refine os prompts do Spring AI para gerar diálogos realistas e contextualizados.
- **Fullstack Dev:** Implemente a integração entre os logs de performance no MongoDB e o dashboard Streamlit.
