#!/bin/bash
# sdd.sh – Orquestração SDD com Spec Kit + modelos locais

set -e

FEATURE_DESC="$1"
if [ -z "$FEATURE_DESC" ]; then
    echo "Uso: ./sdd.sh \"descrição da feature\""
    exit 1
fi

echo "🚀 Iniciando SDD para: $FEATURE_DESC"

# 1. Criar branch e diretório da feature usando script do Spec Kit
echo "📁 Criando estrutura da feature..."
SCRIPT_DIR=".specify/scripts/bash"
FEATURE_DIR=$($SCRIPT_DIR/create-new-feature.sh --json "$FEATURE_DESC" | jq -r '.feature_dir')
echo "Feature directory: $FEATURE_DIR"

# 2. Escrever spec.md usando o agente plan
echo "📝 Gerando spec.md..."
opencode run --agent plan --dangerously-skip-permissions "
Leia o constitution em .specify/memory/constitution.md.
Crie o arquivo $FEATURE_DIR/spec.md seguindo o template do Spec Kit (veja em .specify/templates/spec-template.md).
A feature é: $FEATURE_DESC

Use o formato padrão: User Story, Acceptance Criteria, Functional Requirements, Out of Scope.
"

# 3. Escrever plan.md usando o agente plan
echo "📐 Gerando plan.md..."
opencode run --agent plan --dangerously-skip-permissions "
Com base em $FEATURE_DIR/spec.md, crie o arquivo $FEATURE_DIR/plan.md.
Inclua: stack tecnológico (Python, FastAPI, etc.), arquitetura, decisões técnicas.
"

# 4. Escrever tasks.md usando o agente plan
echo "📋 Gerando tasks.md..."
opencode run --agent plan --dangerously-skip-permissions "
Com base em $FEATURE_DIR/spec.md e $FEATURE_DIR/plan.md, crie $FEATURE_DIR/tasks.md.
Divida em tarefas pequenas e executáveis, cada uma com um checkbox [ ].
"

# 5. Implementar código usando o agente build
echo "💻 Implementando código..."
opencode run --agent build --dangerously-skip-permissions "
Implemente o código necessário para a feature descrita em $FEATURE_DIR/spec.md e $FEATURE_DIR/tasks.md.
Use Python com FastAPI. Coloque o código em src/.
Respeite o plano em $FEATURE_DIR/plan.md.
"

echo "✅ SDD concluído para a feature: $FEATURE_DIR"
