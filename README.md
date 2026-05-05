# Tour Teresina Golf

Mini golfe 2D top-down em Python/Pygame: tacada estilo estilingue (arrastar na direção oposta ao tiro), física simples com atrito, buraco, zonas de água e limite de tacadas — conforme o GDD do projeto académico.

O jogo renderiza internamente em **960×540** (espaço lógico) e **escala** para o tamanho da janela ou ecrã completo.

## Requisitos

- Python 3.10 ou superior (recomendado)
- Windows (alvo principal do GDD)

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

## Controlos

- **Jogo:** apenas rato — clicar perto da bola, arrastar e soltar para tacar.
- **Menu / vitória / game over:** botões com o rato; na intro, **Enter**, **Espaço** ou clique para continuar.
- **Durante o jogo:** **Esc** volta ao menu.
- **Vídeo:** no menu principal, **Opções de vídeo** — alternar ecrã inteiro; em modo **janela**, ver o tamanho em pixels (960×540 × escala) e usar **−** / **+** para mudar a escala (1×…6×).
- Atalhos: **F11** ou **Alt+Enter** (fullscreen); **[** / **]** ou **-** / **=** (escala só em janela).
- Preferências ficam em **`user_settings.json`** (`fullscreen`, `window_scale`, `settings_version`). Se o jogo abrir em modo estranho após testes antigos, apaga este ficheiro para voltar aos padrões (janela, escala 2×).

## Empacotar (.exe)

Instale o PyInstaller no ambiente virtual e gere o executável (ajuste caminhos se necessário):

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --name TourTeresinaGolf main.py
```

O binário aparece em `dist/`. Inclua eventualmente ícone com `--icon=caminho.ico`.

## Estrutura

- `main.py` — entrada
- `tour_teresina_golf/` — pacote (`app`, física, colisão, vídeo, `settings`, nível de teste, ecrãs)
- `user_settings.json` — criado automaticamente (preferências de janela)
- `PENDENCIAS.md` — itens ainda por implementar face ao GDD completo
