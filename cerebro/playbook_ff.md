# PLAYBOOK UNIVERSAL - Trabalhar com QUALQUER versao do Free Fire

Regra 0: nunca mexa no APK sem fazer copia. Guardar sha256 dos arquivos originais.

## FASE 1 - Reconhecer a geracao do APK
1. `unzip -l jogo.apk | grep -E "lib/|dex|metadata"` — ver arquiteturas (armeabi, armeabi-v7a, arm64-v8a) e quantos dex.
2. 32-bit puro (2018): so roda em celular 32-bit ou com suporte. Se o Redmi for 64-bit only, crash na hora sem nem logo.
3. Unity IL2CPP: tem `assets/bin/Data/Managed/Metadata/global-metadata.dat` — strings do jogo C# vivem LA.
4. SDK de login da Garena: `com/beetalk/sdk/` nos smali (versoes ~2019-2022).

## FASE 2 - Decompilar
1. Rapido (so smali): `apktool d -s jogo.apk -o jogo_smali`
2. Completo (com resources): `apktool d jogo.apk -o jogo_full`
3. Se apktool falhar em resources: `unzip jogo.apk -d jogo_raw` e trabalhar nos binarios direto.
4. Termux: `pkg install apktool openjdk-17` antes.

## FASE 3 - Achar TODOS os enderecos de servidor
1. `grep -rhoa 'https\?://[^"<> ]\{5,60\}' pasta/ | sort -u` — em smali, metadata e manifest.
2. Lugares obrigatorios de olhar:
   - classes.dex / classes2.dex / classes3.dex (strings do SDK Java)
   - assets/bin/Data/Managed/Metadata/global-metadata.dat (strings C#/Unity)
   - AndroidManifest.xml (meta-data, TP shell, providers)
   - assets/*.json e *.xml de config
3. Endereco do lobby geralmente aparece em: SDKConstants.smali (2.19.2+), ou literal `http://IP:PORTA` (2018).

## FASE 4 - Saber o que o servidor deve responder
1. Se o servidor ORIGINAL ainda viver: `curl` em cada rota e salvar resposta REAL.
2. Contrato Garena SDK (vale pra quase toda versao):
   - POST /oauth/guest/register (uid/device_id) → {open_id, platform:4, nickname, access_token, refresh_token, expires_in}
   - POST /oauth/guest/token/grant, /oauth/token (grant_type), /oauth/token/inspect
   - GET /oauth/user/info/get?access_token=... → dados do player
   - GET /me, /ver.php, /app/info/get, /api/heartbeat, /api/msdk
   - /live/* (lobby 2018), /oauth/logout
3. Servidor espelho base: ff2018_server.js (Node puro, arquivo unico, sem dependencia).

## FASE 5 - Remendar o APK (A REGRA MAIS IMPORTANTE)
OPCAO A (cirurgia de bytes — rapida, zero recompile):
- So serve se o novo endereco tiver O MESMO NUMERO DE BYTES do antigo.
- Truques pra ganhar bytes: porta com zeros a esquerda (Java/.NET aceitam `:0000018000`).
- `https://rzim2018.vercel.app` = 27 bytes = mesmo tamanho de `http://190.115.198.51:18000`.
- Nunca usar sed com string de tamanho diferente em dex/metadata BINARIO — corrompe offsets e crasha.
- Depois de trocar: conferir header do dex: file_size (bytes 32-36, little endian) == tamanho real do arquivo.

OPCAO B (smali + recompile — flexivel, para mudar qualquer coisa):
1. Decompilar SO o dex alvo: `apktool d -f --no-res classes3.dex` (renomear pra .zip antes se apktool reclamar).
2. Editar os .smali (smali = assembly do Dalvik, da pra ler).
3. Recompilar: `apktool b pasta -o novo.zip` e extrair o classes.dex.
4. Trocar o dex dentro do APK (python zipfile, item por item, preservando compress_type).
5. Se o rebuild der dex corrompido: `rm -rf pasta/build` e rebuildar de novo.

## FASE 6 - Anticheats (toda versao de mod baixada pode ter)
1. Procurar por portao de verificacao: activity launcher no AndroidManifest + classes tipo `anticheatclaude`, `Portao`, `Guarda`, `Verificador`.
2. Esses portoes validam: hash do APK inteiro, assinatura, libs nativas com sha selado (`lib*.so` + hash no smali). QUALQUER byte mudado → tela preta/bloqueio/crash.
3. Bypass classico: neutralizar os metodos de decisao no smali (permitido/aprovado/verificado → `const/4 v0, 0x1; return v0`; bloqueado → `const/4 v0, 0x0; return v0`; hooks de checagem → `return-void`) e recompilar o dex.
4. Ganchos tipicos: onCreate de cada activity (`UnityPlayerActivity`, `FFMainActivity`), onResume (checagem pos-inicio), attachBaseContext do Application (TP Shell `libtprt.so`).
5. TP Shell Tencent: carrega `libtprt.so` cedo (PreInicio); se ele exige servidor proprio (meta-data no manifest), esse servidor precisa existir ou o hook precisa ser neutralizado.
6. Servidores de anticheat de mods antigos costumam estar MORTOS — o mod original pode nem ligar mais. Testar: `curl -m 10 http://IP:PORTA`.

## FASE 7 - Assinar e testar
1. `java -jar uber-apk-signer.jar -a jogo_remendado.apk` (gera *-aligned-debugSigned.apk).
2. Sanity: dex headers batendo, APK abre no apksigner verify [v1,v2,v3].
3. Instalar no celular: se crashar ANTES da logo → anticheat ou 32-bit; se travar na tela de login → servidor nao respondeu certo; se logar e travar no lobby → rota /live ou de jogo faltando.
4. Ver logs: `adb logcat | grep -i "AndroidRuntime\|Unity"` ou no Termux `logcat -d | tail`.

## FASE 8 - Deixar o servidor no ar
1. Termux no celular (APK aponta pra 127.0.0.1): node ff2018_server.js + termux-wake-lock + Termux:Boot.
2. Vercel gratis (dominio precisa caber no remendo): projeto serverless, vercel.json com rewrites catch-all → api/ff.js.
3. Railway: cuidado, trial de $5 esgota e trava o workspace todo.
4. Cloudflare Tunnel no notebook: dominio fixo, mas trycloudflare.com e grande demais pro remende de bytes — precisa de dominio curto proprio.

## ERROS COMUNS (aprendidos na pele)
- sed em dex binario com tamanho diferente → APK corrompido, crash instantaneo.
- Esquecer de remendar global-metadata.dat → jogo loga mas nao acha o lobby.
- Assinatura sem zipalign → alguns Androids recusam.
- Mod 32-bit em celular sem suporte 32-bit → crash antes de tudo.
- Recompilar dex com build/ velho na pasta → apktool usa dex antigo.
- Trocar a URL so num arquivo → SDK Java e engine Unity usam enderecos DIFERENTES.
