# llm-representation

Come "vedono" i modelli di linguaggio?
Guardiamo dentro un modello piccolo ([Qwen3.5-0.8B-Base](https://huggingface.co/Qwen/Qwen3.5-0.8B-Base)):

- **Testo.** Ogni parola diventa un vettore (embedding). Guardiamo come il vettore cambia da un layer all'altro.
- **Immagini.** Una foto si divide in patch da 16 pixel. Ogni gruppo di 2x2 patch diventa un token. Il modello tratta questi token come parole.

## Cosa trovi

Un solo notebook: `llm-representation.ipynb`.

## Prima di iniziare

Controlla di avere:

- un Mac con Apple Silicon;
- `uv` e `git` (`brew install uv git`);
- internet e alcuni GB di spazio libero;
- la camera: facoltativa (vedi sotto).

## Passo per passo

1. Apri il Terminale.

2. Scarica la repo ed entra nella cartella:

   ```bash
   git clone https://github.com/pierpierpy/smanettiamo
   cd smanettiamo/llm-representation
   ```

3. Avvia JupyterLab:

   ```bash
   uv run jupyter lab
   ```

   Il primo avvio dura alcuni minuti. `uv` installa Python 3.12 e le librerie.
   Quando finisce, il browser si apre. Se non si apre, copia nel browser il link che inizia con `http://localhost:8888/`.

4. Nel pannello a sinistra fai doppio clic su `llm-representation.ipynb`.
   Se JupyterLab chiede il kernel, scegli **Python 3 (ipykernel)**.

5. Esegui le celle in ordine con `Shift + Invio`. Non saltare celle.

6. Alla fine ferma tutto: nel terminale premi `Ctrl + C` due volte.

## Cosa vedi, cella per cella

- **Sezione "Text".** Il notebook scarica `Qwen/Qwen3.5-0.8B-Base` da Hugging Face e lo carica sulla GPU del Mac. Il primo avvio è lento. Poi il testo diventa token. Vedi gli embedding come piccole mappe di colore (32 x 32 = 1024 dimensioni). Poi confronti la stessa parola ("pesca") in due punti della frase. Dopo i 24 layer i due vettori sono diversi: il modello ha capito il contesto.
- **Sezione "Images", prima parte.** Il notebook prende un frame dalla camera (o la foto di esempio). Lo divide in patch da 16 pixel e disegna la griglia dei token.
- **Sezione "Images", seconda parte.** Il notebook carica la versione del modello che legge anche le immagini. Poi dà al modello la foto `data/imgs/carta_1.jpg` e il testo "This is a photo of". Alla fine vedi gli embedding dei token-immagine accanto a quelli del testo.

## La camera (facoltativa)

La sezione "Images" può usare la tua camera. Non devi avviare niente nel terminale: la cella con `start()` avvia la camera.

1. Esegui la cella con `start()`.
2. macOS chiede il permesso per la camera. Premi **Consenti**.
   Se il permesso va a un'altra app, apri *Impostazioni di Sistema > Privacy e sicurezza > Fotocamera* e attiva l'app che avvia Jupyter (di solito Terminale). Poi esegui di nuovo la cella.
3. Vedi il video nel notebook. La cella dopo prende un frame dal video.

Vuoi usare il telefono come camera? Installa l'app DroidCam. Poi cambia la riga nella cella:

```python
start(url="http://<IP-DEL-TELEFONO>:4747/video")   # usa l'indirizzo che l'app mostra
```

Non hai una camera? Non devi fare niente. Se `start()` non riesce, il notebook scrive un messaggio e usa la foto di esempio `data/imgs/carta_1.jpg`.

## Se qualcosa non funziona

| Problema | Cosa fare |
| --- | --- |
| `uv: command not found` | Esegui `brew install uv`. Poi apri un nuovo terminale. |
| Il primo avvio sembra bloccato | Aspetta. Il terminale o il notebook stanno scaricando file grandi. |
| Errore con `mps` | Il tuo Mac non ha Apple Silicon. Questo progetto non funziona su quel Mac. |
| `the camera did not start` | Dai il permesso alla camera (vedi sopra). Oppure vai avanti: il notebook usa la foto di esempio. |
| `camera already running` | Un server webcam è già attivo sulla porta 8090. Il notebook lo usa. Non è un errore. |
| Poca memoria / il Mac rallenta | Chiudi le altre app. Il modello usa `float32` e occupa alcuni GB di RAM. |
| Altri errori | Riavvia il kernel (menu **Kernel > Restart Kernel**) ed esegui le celle dall'inizio. |

## Per chi vuole sapere di più

- Le librerie e le loro versioni sono in `pyproject.toml` e `uv.lock`. Non modificare `uv.lock` a mano.
- Il server webcam è nella cartella `../webcam/`. Il progetto lo installa da solo.
