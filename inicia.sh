#!/data/data/com.termux/files/usr/bin/sh
# Liga a GROQDEV IA dentro de uma sessao tmux (fica rodando em segundo plano)
# Depois de rodar:  tmux attach -t ia   (pra conversar com ela)
# Pra sair sem matar: Ctrl+B e depois D

command -v tmux >/dev/null || { echo "instale: pkg install tmux"; exit 1; }
[ -z "$GROQ_API_KEY" ] && { echo "falta a chave: export GROQ_API_KEY=gsk_..."; exit 1; }

cd "$(dirname "$0")"
tmux has-session -t ia 2>/dev/null && { echo "ja esta rodando. Entre com: tmux attach -t ia"; exit 0; }
tmux new-session -d -s ia "python3 groqdev.py; sleep 3; exec sh"
echo "GROQDEV rodando. Para conversar: tmux attach -t ia"
