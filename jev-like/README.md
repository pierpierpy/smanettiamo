# jev-like

Come funziona JEV. Usiamo [Kev](https://github.com/jaredpalmer/kev): un modello piccolo che prende decisioni.
Poi diamo gli occhi a Kev e lo colleghiamo a una webcam.

## Cosa trovi

| Notebook | Cosa fa | Camera |
| --- | --- | --- |
| `how-jev-works.ipynb` | Dalla richiesta alle probabilità. Poi la "pointer head", passo per passo. In fondo c'è il dataset `kev-suites`. | No |
| `kev-image.ipynb` | Kev con un encoder di immagini (`src/kev_image.py`). Poi la webcam: Kev capisce se usi il telefono e suona una sirena. | Solo nell'ultima parte |

## Prima di iniziare

Controlla di avere:

- un Mac con Apple Silicon;
- `uv` e `git` (`brew install uv git`);
- internet e alcuni GB di spazio libero.

## Passo per passo

1. Apri il Terminale.

2. Scarica la repo ed entra nella cartella:

   ```bash
   git clone https://github.com/pierpierpy/smanettiamo
   cd smanettiamo/jev-like
   ```

3. Avvia JupyterLab:

   ```bash
   uv run jupyter lab
   ```

   Il primo avvio dura alcuni minuti. `uv` installa Python 3.12, le librerie e Kev.
   Quando finisce, il browser si apre. Se non si apre, copia nel browser il link che inizia con `http://localhost:8888/`.

4. Nel pannello a sinistra fai doppio clic su un notebook.
   Se JupyterLab chiede il kernel, scegli **Python 3 (ipykernel)**.

5. Esegui le celle in ordine con `Shift + Invio`. Non saltare celle.

6. Alla fine ferma tutto: nel terminale premi `Ctrl + C` due volte.

## Cosa vedi, cella per cella

- **Prima cella con `Checkpoint(...)`.** Il notebook scarica Kev (`jaredpalmer/kev-0.8b`) e il modello base (`Qwen/Qwen3.5-0.8B-Base`) da Hugging Face. Il primo avvio è lento. Gli avvii dopo sono veloci.
- **`how-jev-works.ipynb`, parte 1.** Una richiesta diventa un testo. Il modello dà una probabilità a ogni risposta possibile.
- **`how-jev-works.ipynb`, parte 2.** La "pointer head" sceglie tra le risposte.
- **`kev-image.ipynb`, sezioni "Text" e "Image".** Prima Kev legge una frase e dice se l'utente è arrabbiato. Poi guarda `data/imgs/carta_1.jpg` e decide in quale bidone va l'oggetto (carta, plastica, vetro, organico, altro).
- **`kev-image.ipynb`, sezione "Streaming from the webcam".** Questa sezione usa la camera. Leggi sotto.

## La webcam (facoltativa)

Solo l'ultima parte di `kev-image.ipynb` usa la camera. Non devi avviare niente nel terminale: la cella con `start()` avvia la camera.

1. Esegui la cella con `start()`.
2. macOS chiede il permesso per la camera. Premi **Consenti**.
   Se il permesso va a un'altra app, apri *Impostazioni di Sistema > Privacy e sicurezza > Fotocamera* e attiva l'app che avvia Jupyter (di solito Terminale). Poi esegui di nuovo la cella.
3. Vedi il video nel notebook. Esegui le celle dopo, fino a "Live loop".
4. Nel "Live loop" prendi il telefono in mano davanti alla camera. Kev lo vede e parte la sirena.
5. Per fermare il loop premi il pulsante **Interrupt** (il quadrato) in alto nel notebook.

Vuoi usare il telefono come camera? Installa l'app DroidCam sul telefono. Poi cambia la riga nella cella:

```python
start(url="http://<IP-DEL-TELEFONO>:4747/video")   # usa l'indirizzo che l'app mostra
```

Non hai una camera? Salta la sezione "Streaming from the webcam". Il resto del notebook funziona lo stesso.

La sirena (`assets/nuclear_alarm.mp3`) si scarica da sola la prima volta da BigSoundBank (licenza CC0).

## Se qualcosa non funziona

| Problema | Cosa fare |
| --- | --- |
| `uv: command not found` | Esegui `brew install uv`. Poi apri un nuovo terminale. |
| Il primo avvio sembra bloccato | Aspetta. Il terminale o il notebook stanno scaricando file grandi. |
| Errore con `mps` | Il tuo Mac non ha Apple Silicon. Questo progetto non funziona su quel Mac. |
| `the camera did not start` | Dai il permesso alla camera (vedi sopra). Poi esegui di nuovo la cella con `start()`. |
| `camera already running` | Un server webcam è già attivo sulla porta 8090. Il notebook lo usa. Non è un errore. |
| Il video non appare nel notebook | Ricarica la pagina del browser. Poi esegui di nuovo `show()`. |
| Altri errori | Riavvia il kernel (menu **Kernel > Restart Kernel**) ed esegui le celle dall'inizio. |

## Per chi vuole sapere di più

- Le librerie e le loro versioni sono in `pyproject.toml` e `uv.lock`. Non modificare `uv.lock` a mano.
- Kev è bloccato sul commit `5e42a7a` di [jaredpalmer/kev](https://github.com/jaredpalmer/kev).
- `src/kev_image.py` aggiunge a Kev l'encoder di immagini di Qwen3.5.
