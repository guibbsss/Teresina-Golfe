# Pendências de implementação — Tour Teresina Golf

Este ficheiro lista o que **ainda falta** para alinhar o produto ao [GDD](GDD%20Mini%20Golfe%20Teresina%20(1).pdf) completo e a um lançamento polido. O código atual cobre um **MVP jogável** (motor, uma fase de teste, fluxo de ecrãs, vídeo configurável).

---

## Relativo ao GDD — o que já cobre o documento (resumo)

- **Sec. 2 — Controles:** rato, estilingue (clicar na bola, arrastar na direção oposta ao tiro, soltar).
- **Sec. 2 — Vitória / derrota:** tacadas limitadas; água → game over; buraco com velocidade baixa (`HOLE_WIN_SPEED_SQ`) ou paragem no raio.
- **Sec. 2 — Física:** velocidade, atrito, colisões com obstáculos rectangulares.
- **Sec. 5 — HUD (parcial):** tacadas restantes e nome da fase visíveis (ver **desvio** abaixo).
- **Sec. 7 — Stack:** Python 3 + Pygame; notas de build PyInstaller no README.

---

## Sec. 2 — Sistema de pontuação / ranking

- O GDD prevê **ranking baseado em menos tacadas** por fase / circuito.
- **Em falta:** persistência (ficheiro local ou tabela), ecrã ou secção de **ranking**, comparar sessões ou nome do jogador (opcional).

---

## Sec. 3 — Game loop macro

- **Em falta:** fluxo **Mirar → obstáculo da rua/ponte → buraco → próximo ponto turístico** com **três layouts** distintos e **dificuldade crescente**.
- **Em falta:** motivação explícita **“topo do ranking”** ligada ao sistema de pontuação acima.

---

## Sec. 5 — Level design (três cenários turísticos)

- **Fase 1 — Avenida Frei Serafim:** corredor com canteiros centrais como no esboço; hoje há só **fase de teste** genérica (`make_test_level`).
- **Fase 2 — Ponte Estaiada:** **vãos**, **paredes diagonais** (estais), necessidade de **quiques**; falta motor de colisão **círculo–segmento** (ou equivalente) e nível desenhado.
- **Fase 3 — Encontro dos Rios:** obstáculo **estátua Cabeça de Cuia** (intransponível); **água** narrativa **Poti / Parnaíba** (há zonas de água genéricas, falta cenário e layout finais).
- **Progressão:** **Menu → Fase 1 → Fase 2 → Fase 3 → Tela de Vitória** global; falta encadear níveis e **ecrã de vitória final** do circuito (além da vitória por buraco na sessão actual).

---

## Sec. 5 — HUD (mockup vs implementação)

- O GDD indica **“Tacadas Restantes” no canto superior esquerdo** e **“Fase Atual” no canto superior direito**.
- **Implementação actual:** ambas as linhas num **único painel** no canto **superior esquerdo** (legibilidade e escala). Pendência opcional: **repor layout em dois cantos** como no mockup, se preferires aderência visual estrita ao PDF.

---

## Sec. 6 — Estética e áudio

- **Pixel art top-down** com assets **gratuitos** (ex.: Itch.io), clima quente, asfalto, verdes — ainda em grande parte **placeholders** geométricos.
- **SFX (GDD):** elástico ao arrastar mira; tacada seca; impacto em paredes/**estátua**; splash na água — hoje há **`audio_stub`** sem ficheiros sonoros.
- **Música:** chiptune descontraído em loop — **não implementado**.
- **Moodboard / imagens de referência** do PDF: incorporar na direção de arte quando os assets estiverem escolhidos.

---

## Sec. 7 — Planeamento técnico e distribuição

- **PyInstaller / .exe:** instruções no README; falta **validação** numa máquina limpa e eventual **ícone** do executável.
- **Itch.io / assets:** integração pendente conforme cronograma do GDD.
- **Parâmetros de física** editáveis via **JSON/TOML** sem recompilar — opcional (ainda não feito).

---

## UX / polish adicional (não obrigatório no PDF mas útil)

- **Créditos** com nomes da equipa do GDD (capa do documento).
- **Volume** e, se desejado, **sensibilidade / força máxima** da tacada nas Opções (além do vídeo já existente).
- **Tutorial** ou dica na primeira tacada.

---

## Riscos / dependências

- Colisões com **paredes diagonais** e **vãos** na Ponte Estaiada: mais testes anti-tunneling e tuning.
- Arte e áudio dependentes de escolha de assets e licenças.
