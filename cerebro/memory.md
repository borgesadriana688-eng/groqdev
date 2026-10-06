# Cerebro da GROQDEV

- Dono: Brayan. Lingua: portugues (BR). Ambiente de trabalho: Termux no Android + notebook.
- Projetos ativos: FF2018 (Free Fire 2018 private server), Freefire Private 2.19.2, Battle Engine (C/SDL2), Godot 4.6.1.

## FF2018 - o que ja sabemos (aprendido em out/2026)
- APK base: 1.25.3 do Barbosa Tech (445MB), apontava para 190.115.198.51:18000 (vivo).
- Servidor de login deles responde em rotas Garena: /oauth/guest/register, /oauth/guest/token/grant, /oauth/token, /oauth/token/inspect, /oauth/user/info/get, /me, /ver.php, /app/info/get ({"status":0,"client_log":false}), /api/heartbeat, /api/msdk, /live/*.
- Nosso servidor espelho: ff2018_server.js (Node puro, sem dependencias) e versao serverless em github.com/borgesadriana688-eng/rzim2018-server (Vercel, dominio rzim2018.vercel.app).
- Remendo de URL no APK: cirurgia de bytes de MESMO tamanho. "http://190.115.198.51:18000" tem 27 bytes; "https://rzim2018.vercel.app" tambem tem 27. Trocar em classes.dex (2x) + global-metadata.dat (1x). NUNCA usar sed com strings de tamanho diferente em dex (quebra offsets e crasha).
- Anticheats do APK 2018: (1) Portao/Guarda do Barbosa em classes3.dex (anticheatclaude): valida APK+assinatura+libantidoente.so e trava se mudar 1 byte. Bypass: neutralizar Guarda.smali (permitido/aprovadoNesteProcesso/conferirDepois=true, bloqueadoDepois=false, aposInicio=no-op) e recompilar classes3.dex. (2) TP Shell Tencent (libtprt.so) carregado no boot via PreInicio.
- Servidor de anticheat deles (122.11.128.69:2205) esta MORTO.
- Ferramentas no notebook do agente: apktool, uber-apk-signer, JDK17, python3.

## Como responder
- Direto ao ponto, passo-a-passo numerado, comandos prontos pra copiar.
- Se nao souber algo do APK, DECOMPILE e descubra com bash/grep em vez de chutar.


## PLAYBOOK OBRIGATORIO
- Antes de mexer em QUALQUER APK de Free Fire (qualquer versao), LEIA cerebro/playbook_ff.md com read_file.
- Ele tem as 8 fases completas: reconhecer geracao, decompilar, achar enderecos, contrato do servidor, remendo de bytes vs smali+recompile, anticheats, assinatura, hospedar.
- Erros comuns que crasham APK estao listados la (sed em dex binario, 32-bit, metadata esquecido).
