# smanettiamo

Questa repo contiene i progetti dei miei video su YouTube.
Ogni progetto è un notebook Jupyter. Apri il notebook, esegui le celle e guarda cosa succede.

| Cartella | Di cosa parla | Notebook |
| --- | --- | --- |
| [`jev-like/`](jev-like/README.md) | Come funziona JEV. Usiamo Kev, un modello piccolo che prende decisioni. Nella seconda parte Kev guarda una webcam e capisce se stai usando il telefono. | `how-jev-works.ipynb`, `kev-image.ipynb` |
| [`llm-representation/`](llm-representation/README.md) | Come "vedono" i modelli di linguaggio. Guardiamo cosa succede dentro il modello con un testo e con una foto. | `llm-representation.ipynb` |

## Cosa serve

- Un Mac con chip Apple Silicon (M1 o più nuovo). I notebook usano la GPU del Mac (`mps`).
- Una connessione a internet. Il primo avvio scarica i modelli da Hugging Face. Servono alcuni GB di spazio libero.
- [`uv`](https://docs.astral.sh/uv/) e `git`.
- Una camera: facoltativa. Senza camera usi le foto nella cartella `data/imgs/`.

Installa `uv` e `git` con Homebrew:

```bash
brew install uv git
```

## Come iniziare

Usi il terminale solo due volte. Poi lavori nel notebook.

1. Scarica la repo ed entra nella cartella del progetto che vuoi provare:

   ```bash
   git clone https://github.com/pierpierpy/smanettiamo
   cd smanettiamo/jev-like        # oppure: cd smanettiamo/llm-representation
   ```

2. Avvia JupyterLab:

   ```bash
   uv run jupyter lab
   ```

   Il primo avvio è lento: `uv` crea l'ambiente e scarica le librerie. Il browser si apre da solo.

3. Nel browser apri il notebook dal pannello a sinistra. Esegui le celle una dopo l'altra con `Shift + Invio`.

Per i dettagli, leggi il README del progetto.

## Webcam

La camera serve solo nelle sezioni "live". Il notebook la avvia da solo con `webcam.start()`.
Non devi usare il terminale per questo.

- Camera del Mac: `start()`. macOS chiede il permesso la prima volta.
- Telefono con l'app DroidCam: `start(url="http://<IP-DEL-TELEFONO>:4747/video")`.
- Il server ascolta solo su `127.0.0.1:8090`. Non ha password. Nessun altro computer può usarlo.

## Usi un agente AI?

Un agente (Kiro, Claude Code, Codex, ...) può preparare tutto per te. Digli di leggere [`AGENTS.md`](AGENTS.md).

## Licenze

- Il codice di questa repo usa la licenza MIT (vedi `LICENSE`).
- [Kev](https://github.com/jaredpalmer/kev) usa la licenza Apache-2.0. Il notebook lo scarica come dipendenza.
- I modelli Qwen e Kev hanno le loro licenze su Hugging Face. Leggile prima di usarli per altro.
