#!/bin/bash

VERSION=$1
NOMEENV=$2

# Instala o pyenv-virtualenv se ainda não tiver
brew install pyenv-virtualenv

# Inicializa o pyenv (recomendado incluir isso no .zshrc permanentemente)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Instala o Python especificado, se necessário
pyenv install -s $VERSION

# Cria o ambiente virtual
pyenv virtualenv $VERSION $NOMEENV

# Ativa o ambiente virtual
pyenv activate $NOMEENV

# Confirmação
echo "✅ Ambiente '$NOMEENV' ativado com Python $VERSION"

#sugesgtao 3.11.9
