# GROQDEV - IA programadora com cerebro (API Groq)

IA de programacao e engenharia reversa que roda no Termux, 100% Python puro
(sem pip install), com memoria permanente e ferramentas de verdade (bash, arquivos).

## Instalacao (2 minutos)
1. Pegue a chave GRATIS em console.groq.com/keys
2. No Termux:
   export GROQ_API_KEY=gsk_sua_chave
3. Ligue:
   sh inicia.sh
4. Converse:
   tmux attach -t ia
   (pra sair sem desligar: Ctrl+B e depois D)

## Abrir um APK no cerebro dela
python3 groqdev.py --apk caminho/do.apk
(elo decompila com apktool, indexa manifest/urls/arquivos e salva tudo na memoria)

## O que ela sabe fazer
- Decompilar e analisar APK (apktool precisa estar instalado: pkg install apktool)
- Ler, escrever e executar codigo
- Criar servidores e testar eles sozinha
- Lembrar pra sempre tudo que descobre (cerebro/memory.md)

## Playbook universal
tem cerebro/playbook_ff.md: guia completo pra reviver QUALQUER versao do Free Fire (8 fases + erros comuns). A IA le automaticamente antes de mexer em APK.

## Cerebro
O arquivo cerebro/memory.md e a memoria permanente dela.
Ja vem carregada com tudo do projeto FF2018 (endpoints, bypass de anticheat, macete do remendo de bytes).

## Modelo
Usa llama-3.3-70b-versatile por padrao. Para trocar:
export GROQ_MODEL=openai/gpt-oss-120b
