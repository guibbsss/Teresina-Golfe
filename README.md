# Tour Teresina Golf

Mini golfe 2D top-down em Python/Pygame: tacada estilo estilingue, física com
atrito, buraco, zonas de água e sistema de estrelas — ambientado nos pontos
turísticos de Teresina (PI).

## Download

> **[Baixar TourTeresinaGolf.exe](https://github.com/guiri/Teresina-Golfe/releases/latest/download/TourTeresinaGolf.exe)**

Substitui o segmento `guiri/Teresina-Golfe` na URL pelo teu utilizador e repositório reais no GitHub antes de publicar o release.

Apenas Windows 64-bit. Não requer instalação — executa o `.exe` diretamente.
O progresso (`save_data.json`) fica salvo na mesma pasta do executável.

---

## Executar pelo código-fonte

**Requisitos:** Python 3.10+ e pip.

```bash
pip install -r requirements.txt
python main.py
```

Para saltar para uma fase específica:

```bash
python main.py fase2
python main.py fase3
```

---

## Gerar o executável (.exe)

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm TourTeresinaGolf.spec
```

Ou usa o script:

```text
build.bat
```

### Onde fica a build

Após o PyInstaller terminar, o **executável do jogo** fica na pasta **`dist/`**, na **raiz do repositório** (ao lado de `main.py` e do ficheiro `.spec`):

- **Windows:** `dist\TourTeresinaGolf.exe`

A pasta **`build/`** (também na raiz) contém apenas ficheiros temporários do PyInstaller; o que se distribui ou se executa fora do Python é o conteúdo de **`dist/`**.

---

## Controlos

| Ação | Controle |
|------|----------|
| Tacar | Clicar perto da bola, arrastar, soltar |
| Pausar | ESC durante o jogo |
| Tela cheia | F11 ou Alt+Enter |
| Escala da janela | `[` diminui / `]` aumenta (modo janela) |

---

## Fases

| Fase | Nome | Tacadas |
|------|------|---------|
| 1 | Avenida Frei Serafim | 10 |
| 2 | Ponte Estaiada | 12 |
| 3 | Encontro dos Rios | 15 |

---

## Equipe

- Gabriel Lages Oliveira de Azevedo — Programação e Física
- Guilherme Ruben Pereira Matos — Assets e Level Design

Turma Zeta, 7º Período — ICEV
