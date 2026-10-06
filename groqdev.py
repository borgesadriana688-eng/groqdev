#!/usr/bin/env python3
# ============================================================
# GROQDEV - IA programadora reversa (agente com ferramentas)
# 100% Python puro (stdlib), roda em Termux sem pip install.
# Chave: console.groq.com/keys (grátis)
# Uso:
#   export GROQ_API_KEY=gsk_...
#   python3 groqdev.py                 # chat
#   python3 groqdev.py --apk jogo.apk  # abre APK no cérebro
# ============================================================
import json, os, sys, subprocess, urllib.request

API = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
KEY = os.environ.get("GROQ_API_KEY", "")
CEREBRO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cerebro")
MEMORIA = os.path.join(CEREBRO, "memory.md")

TOOLS = [
    {"type":"function","function":{"name":"bash","description":"Executa um comando no shell (Linux/Termux). Use para explorar arquivos, rodar scripts, decompilar APK, etc.","parameters":{"type":"object","properties":{"cmd":{"type":"string"}},"required":["cmd"]}}},
    {"type":"function","function":{"name":"read_file","description":"Le um arquivo de texto do workspace","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"write_file","description":"Cria ou sobrescreve um arquivo com o conteudo dado","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"remember","description":"Salva um fato/aprendizado PERMANENTE no cerebro (memory.md). Use para tudo que descobrir de importante.","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"recall","description":"Recupera toda a memoria permanente do cerebro","parameters":{"type":"object","properties":{}}}},
]

def sys_prompt():
    mem = ""
    if os.path.exists(MEMORIA):
        mem = open(MEMORIA, encoding="utf-8", errors="replace").read()[:8000]
    return (
        "Voce e a GROQDEV, uma IA programadora e engenheira reversa brasileira. "
        "Responda sempre em portugues do Brasil, de forma direta e pratica. "
        "Voce trabalha num terminal Linux/Termux e TEM FERRAMENTAS: use bash, read_file, write_file, remember e recall "
        "para investigar e construir coisas de verdade, nao apenas falar. "
        "Ao aprender algo importante (endpoints, estrutura de APK, senhas de servidor, decisoes), "
        "salve com remember() para nunca mais esquecer. "
        "Voce opera do zero: se pedirem para abrir um APK, decompile com apktool; "
        "se pedirem um servidor, escreva e teste o codigo com bash antes de entregar. "
        "Se uma tarefa falhar, tente outro caminho antes de desistir.\n\n"
        "=== MEMORIA PERMANENTE ===\n" + mem
    )

def llm(messages, tools=None):
    body = {"model": MODEL, "messages": messages, "temperature": 0.3, "max_tokens": 8192}
    if tools: body["tools"] = tools
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["choices"][0]["message"]

def tool_exec(name, args):
    if name == "bash":
        try:
            p = subprocess.run(["sh", "-c", args.get("cmd","")], capture_output=True, text=True, timeout=600)
            out = (p.stdout or "") + (("\n[stderr] " + p.stderr) if p.stderr else "")
            return (out or "(sem saida)")[:12000]
        except Exception as e:
            return "ERRO: " + str(e)
    if name == "read_file":
        try:
            return open(args["path"], encoding="utf-8", errors="replace").read()[:15000]
        except Exception as e:
            return "ERRO: " + str(e)
    if name == "write_file":
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args["path"])) or ".", exist_ok=True)
            open(args["path"], "w", encoding="utf-8").write(args.get("content",""))
            return "arquivo escrito: " + args["path"]
        except Exception as e:
            return "ERRO: " + str(e)
    if name == "remember":
        os.makedirs(CEREBRO, exist_ok=True)
        with open(MEMORIA, "a", encoding="utf-8") as f:
            f.write("\n- " + args.get("text","").strip() + "\n")
        return "memoria salva."
    if name == "recall":
        return open(MEMORIA, encoding="utf-8", errors="replace").read()[:12000] if os.path.exists(MEMORIA) else "(cerebro vazio)"
    return "ferramenta desconhecida"

def agir(msg_inicial, historico):
    messages = historico + [{"role": "user", "content": msg_inicial}]
    for _ in range(12):
        resp = llm(messages, TOOLS)
        calls = resp.get("tool_calls")
        if not calls:
            messages.append(resp)
            return resp.get("content", "(sem resposta)")
        messages.append(resp)
        for c in calls:
            fn = c["function"]["name"]
            args = json.loads(c["function"].get("arguments") or "{}")
            print(f"  [ferramenta] {fn}...")
            resultado = tool_exec(fn, args)
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": resultado})
    return "(limite de iteracoes atingido)"

def ingest_apk(apk):
    os.makedirs(CEREBRO, exist_ok=True)
    pasta = os.path.join(CEREBRO, "apk")
    print("[ingest] decompilando com apktool (demora em APK grande)...")
    r = subprocess.run(["apktool", "d", "-f", "-s", apk, "-o", pasta], capture_output=True, text=True)
    if r.returncode != 0:
        print("[ingest] apktool falhou:", (r.stderr or "")[-300:], "-> tentando unzip simples")
        subprocess.run(["unzip", "-o", apk, "-d", os.path.join(CEREBRO, "apk_raw")], capture_output=True)
        pasta = os.path.join(CEREBRO, "apk_raw")
    idx = os.path.join(CEREBRO, "index.txt")
    cmds = (
        f"echo '== MANIFEST ==' >> {idx}; cat {pasta}/AndroidManifest.xml >> {idx} 2>/dev/null; "
        f"echo '== ARQUIVOS ==' >> {idx}; find {pasta} -type f | head -400 >> {idx}; "
        f"echo '== STRINGS/URLS ==' >> {idx}; grep -rhoa 'https\\?://[^\"<> ]\\{{5,60\\}}' {pasta} 2>/dev/null | sort -u | head -200 >> {idx}"
    )
    subprocess.run(["sh", "-c", cmds])
    with open(MEMORIA, "a", encoding="utf-8") as f:
        f.write(f"\n- APK INGERIDO: {os.path.basename(apk)} decompilado em {pasta}; indice em {idx}\n")
    print(f"[ingest] pronto. Indice: {idx}")
    print("[ingest] rode: python3 groqdev.py  e pergunte 'o que voce sabe sobre o APK?'")

def main():
    global KEY
    if "--apk" in sys.argv:
        ingest_apk(sys.argv[sys.argv.index("--apk") + 1])
        return
    if not KEY:
        print("Falta a chave. Rode antes: export GROQ_API_KEY=gsk_sua_chave (console.groq.com/keys)")
        sys.exit(1)
    print("=== GROQDEV IA ===  (modelo: " + MODEL + " | cerebro: " + MEMORIA + ")")
    print("Comandos: /memoria (ver cerebro) | /sair\n")
    historico = []
    while True:
        try:
            msg = input("voce> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[tchau]")
            break
        if not msg: continue
        if msg == "/sair": break
        if msg == "/memoria":
            print(open(MEMORIA, encoding="utf-8", errors="replace").read() if os.path.exists(MEMORIA) else "(vazio)")
            continue
        try:
            resp = agir(msg, historico)
        except Exception as e:
            resp = "ERRO na chamada da Groq: " + str(e)
        print("ia> " + resp + "\n")
        historico.append({"role": "user", "content": msg})
        historico.append({"role": "assistant", "content": resp})
        historico = historico[-20:]

if __name__ == "__main__":
    main()
