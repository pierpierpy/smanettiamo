# AGENTS.md

Istruzioni per un agente AI che aiuta un utente a usare questa repo.
Rispondi nella lingua dell'utente. I README della repo sono in italiano.

## Cos'è la repo

Due progetti di video YouTube. Ogni progetto è un notebook Jupyter con un ambiente `uv` suo.

| Cartella | Notebook | Modelli (da Hugging Face) |
| --- | --- | --- |
| `jev-like/` | `how-jev-works.ipynb`, `kev-image.ipynb` | `jaredpalmer/kev-0.8b`, `Qwen/Qwen3.5-0.8B-Base`, dataset `jaredpalmer/kev-suites` |
| `llm-representation/` | `llm-representation.ipynb` | `Qwen/Qwen3.5-0.8B-Base` |

Altre cartelle: `webcam/` (server camera, pacchetto `yt-webcam`) e `data/imgs/` (foto di esempio).

## Regola principale

L'utente deve usare **solo il notebook**. Il terminale serve per due comandi: `git clone` e `uv run jupyter lab`.
Non chiedere all'utente altri comandi. Se un passo manca, aggiungilo al notebook o al README, non al terminale dell'utente.

## Requisiti: controllali prima

```bash
uname -sm          # deve essere: Darwin arm64 (Mac con Apple Silicon)
uv --version       # se manca: brew install uv
git --version
```

- I notebook usano `mps` (GPU Apple). Su Linux, Windows o Intel Mac **non funzionano**. Dillo all'utente e fermati.
- Python 3.12 arriva da `uv` in automatico (`.python-version`). Non installare Python a mano.

## Come avviare (sequenza esatta)

1. Scegli il progetto: `jev-like` o `llm-representation`.
2. Entra nella cartella del progetto: `cd <repo>/<progetto>`.
3. Avvia JupyterLab **in background** e non bloccare il terminale:

   ```bash
   uv run jupyter lab --no-browser > /tmp/jupyter.log 2>&1 &
   ```

4. Leggi il link con il token da `/tmp/jupyter.log` (riga `http://localhost:8888/lab?token=...`) e dallo all'utente.
   Se l'utente preferisce, avvia senza `--no-browser`: il browser si apre da solo.
5. Dì all'utente: apri il notebook, kernel **Python 3 (ipykernel)**, esegui le celle in ordine (`Shift + Invio`).

Il primo avvio è lento: `uv` crea il venv, installa le librerie, scarica Kev da GitHub. Poi i notebook scaricano i modelli (alcuni GB). Avvisa l'utente **prima** del download.

## Regole per l'ambiente

- Usa solo `uv`. Non usare `pip install`, `conda` o `python -m venv`.
- Non modificare `uv.lock` a mano. Non eseguire `uv lock --upgrade` o `uv sync --upgrade` se l'utente non lo chiede.
- Per cambiare una dipendenza: modifica `pyproject.toml` del progetto, poi `uv lock` in quella cartella e prova il notebook.
- Kev è bloccato sul commit `5e42a7a03f28134853dd3ff77461457e921e5ec1` in `jev-like/pyproject.toml`. Non cambiarlo senza un motivo: il notebook e `src/kev_image.py` dipendono dall'API di quel commit.
- `webcam/` è un pacchetto locale (`yt-webcam`), installato in modalità editable da `../webcam`. Le modifiche valgono per tutti e due i progetti.

## La webcam

- Il notebook avvia il server da solo con `webcam.start()`. Non lanciare `uv run webcam` in un terminale, se non per debug.
- Senza `webcam/webcam.toml`, `start()` usa la camera del Mac (`device=0`). Per DroidCam: `start(url="http://<IP>:4747/video")`.
- Il server ascolta su `127.0.0.1:8090`, **senza autenticazione**. Non cambiare l'indirizzo in `0.0.0.0` e non aprire la porta verso la rete.
- macOS chiede il permesso per la camera all'app che avvia Jupyter (di solito Terminale). Se `start()` fallisce, guida l'utente in *Impostazioni di Sistema > Privacy e sicurezza > Fotocamera*.
- Se la porta 8090 è occupata: `lsof -nP -iTCP:8090 -sTCP:LISTEN`. `start()` riusa un server già attivo. **Non uccidere** processi senza il consenso dell'utente.
- Altra porta: imposta `WEBCAM_URL=http://localhost:<porta>` prima di avviare Jupyter.
- Senza camera, la sezione "Images" di `llm-representation` usa `data/imgs/carta_1.jpg`. La sezione webcam di `kev-image.ipynb` si può saltare.

## Verifica senza interfaccia (per l'agente)

Esegui un notebook in una copia, **mai in place**:

```bash
cd <repo>/<progetto>
uv run jupyter nbconvert --to notebook --execute <nome>.ipynb --output-dir /tmp/nb-check --ExecutePreprocessor.timeout=1800
```

- `how-jev-works.ipynb` gira da solo (non usa la camera).
- `kev-image.ipynb`: le celle della sezione "Streaming from the webcam" non girano senza camera. Il loop è infinito. Esegui solo le celle prima della sezione.
- `llm-representation.ipynb` gira da solo: senza camera usa la foto di esempio.

## Cose che non devi fare

- Non committare pesi di modelli, `webcam/webcam.toml`, file `.env`, token (GitHub, Hugging Face) o chiavi.
- Non committare notebook con output che contengono foto della webcam o percorsi locali (`/Users/...`). Prima di un commit pulisci gli output:
  `uv run jupyter nbconvert --clear-output --inplace <nome>.ipynb`
- Non usare `git push --force` e non scrivere su `main` senza il consenso dell'utente.
- Non cambiare le chiavi dei modelli (`Qwen/...`, `jaredpalmer/...`) senza dirlo: i risultati nel video dipendono da quei pesi.
- Non esporre JupyterLab o il server webcam sulla rete.

## Problemi comuni

| Sintomo | Causa probabile | Azione |
| --- | --- | --- |
| `uv: command not found` | `uv` non installato | `brew install uv`, nuovo terminale |
| Errore su `mps` | Mac non Apple Silicon | Non supportato: fermati e spiega |
| `the camera did not start` | Permesso camera negato o camera occupata | Guida ai permessi; riprova `start()`; o usa la foto di esempio |
| `camera already running` | Server già attivo su 8090 | Non è un errore: il notebook lo usa |
| Il video non appare in `show()` | `jupyter-server-proxy` non attivo o pagina vecchia | Ricarica la pagina; riesegui `show()`; controlla `/proxy/8090/` |
| Download lento o fallito | Rete o limiti di Hugging Face | Riprova; se serve, `HF_TOKEN` nell'ambiente (mai nei file) |
| Kernel non risponde | Memoria finita (modelli `float32`) | Chiudi altre app; riavvia il kernel |

## Struttura

```
.
├── AGENTS.md
├── README.md                 indice e avvio rapido (IT)
├── data/imgs/                foto di esempio
├── webcam/                   server camera + client per notebook (yt-webcam)
├── jev-like/                 pyproject.toml, uv.lock, src/kev_image.py, 2 notebook, README.md
└── llm-representation/       pyproject.toml, uv.lock, 1 notebook, README.md
```

`jev-like/data` e `llm-representation/data` sono symlink a `../data`.
