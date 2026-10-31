# prefill-decode

Come un modello di linguaggio scrive una risposta? Il lavoro ha due fasi:

- **Prefill.** Il modello legge tutto il prompt in una volta. Per ogni token salva le chiavi e i valori dell'attenzione nella **KV cache**.
- **Decode.** Il modello scrive un token alla volta. Usa la KV cache e non legge di nuovo il prompt.

Usiamo [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) in 4 bit ([`mlx-community/Qwen3-4B-4bit`](https://huggingface.co/mlx-community/Qwen3-4B-4bit)) con [MLX](https://github.com/ml-explore/mlx), la libreria di Apple per la GPU del Mac.
Misuriamo la memoria della KV cache, il tempo del primo token, la velocità con e senza cache e le richieste in parallelo.

## Cosa trovi

Un solo notebook: `prefill-decode.ipynb`. Non usa la camera.

## Prima di iniziare

Controlla di avere:

- un Mac con Apple Silicon (MLX non funziona su altri computer);
- `uv` e `git` (`brew install uv git`);
- internet e circa 3 GB di spazio libero (il modello pesa 2,3 GB);
- almeno 8 GB di RAM.

## Passo per passo

1. Apri il Terminale.

2. Scarica la repo ed entra nella cartella:

   ```bash
   git clone https://github.com/pierpierpy/smanettiamo
   cd smanettiamo/prefill-decode
   ```

3. Avvia JupyterLab:

   ```bash
   uv run jupyter lab
   ```

   Il primo avvio dura alcuni minuti. `uv` installa Python 3.12 e le librerie.
   Quando finisce, il browser si apre. Se non si apre, copia nel browser il link che inizia con `http://localhost:8888/`.

4. Nel pannello a sinistra fai doppio clic su `prefill-decode.ipynb`.
   Se JupyterLab chiede il kernel, scegli **Python 3 (ipykernel)**.

5. Esegui le celle in ordine con `Shift + Invio`. Non saltare celle.

6. Alla fine ferma tutto: nel terminale premi `Ctrl + C` due volte.

## Il modello

Il notebook scarica il modello da solo, nella cella con `load(...)`. Il modello è [`mlx-community/Qwen3-4B-4bit`](https://huggingface.co/mlx-community/Qwen3-4B-4bit) e pesa 2,3 GB.
Il download avviene una sola volta. Hugging Face salva il modello in questa cartella:

```
~/.cache/huggingface/hub/models--mlx-community--Qwen3-4B-4bit
```

Gli avvii dopo leggono il modello da questa cartella. Anche `jev-like` e `llm-representation` salvano i loro modelli in `~/.cache/huggingface/hub`.
Se hai impostato la variabile `HF_HOME`, la cartella è `$HF_HOME/hub`.

### Scaricare il modello a mano (facoltativo)

Vuoi scaricare il modello prima di aprire il notebook? Nella cartella `prefill-decode` esegui:

```bash
uv run hf download mlx-community/Qwen3-4B-4bit
```

`hf` è il programma di Hugging Face per il terminale. `uv` lo installa con le altre librerie del progetto. La prima volta il comando crea anche l'ambiente: dura alcuni minuti.
Alla fine il comando scrive `✓ Downloaded` e il percorso del modello. Il modello va nella cartella di sopra. Poi la cella `load(...)` trova il modello e non lo scarica di nuovo.
Se il download si ferma, esegui di nuovo il comando. Il download riparte da dove si è fermato.

### Liberare spazio

```bash
uv run hf cache ls                                     # mostra i modelli scaricati e quanto pesano
uv run hf cache rm model/mlx-community/Qwen3-4B-4bit   # cancella il modello (chiede conferma)
```

Se dopo esegui di nuovo il notebook, il modello si scarica di nuovo.

## Cosa vedi, cella per cella

- **Sezione "Setup".** Il notebook importa MLX e `mlx-lm` e scrive la memoria della GPU usata (quasi 0 MB).
- **Sezione "Prefill".** La cella con `load(...)` scarica il modello da Hugging Face. Il primo avvio è lento. Gli avvii dopo sono veloci. Poi la frase "ciao io sono Joe! tu come ti chiami?" diventa una lista di token. Il modello legge i token una volta (prefill) e riempie la KV cache. Vedi la forma della cache (layer, richieste, kv heads, token, head dim) e quanti MB occupa. I token usati sono 24 e occupano 3,5 MB. La memoria della GPU sale di 37,7 MB, perché MLX riserva un blocco intero di 256 token.
- **Sezione "Decode e ttft".** Il prompt contiene la parola "casa" 2000 volte. Misuri il tempo del primo token (TTFT) due volte: senza cache il modello legge tutto il prompt; con la cache legge solo l'ultimo token. La differenza è grande.
- **Sezione "Decode senza cache".** Il modello scrive 100 token in due modi. Senza cache, a ogni passo legge di nuovo tutta la frase. Con la cache, legge solo il token nuovo. Il grafico mostra i millisecondi per token: senza cache la linea sale a gradini, con la cache resta piatta.
- **Sezione "Decode streaming".** Prima chiami `next(...)` a mano e vedi un token alla volta. Poi la risposta completa appare mentre il modello la scrive. Sotto vedi i token che restano, i token al secondo e la memoria massima.
- **Sezione "Cache visualization".** Il modello scrive fino a 1000 token. Ogni 100 token il grafico si aggiorna: token che restano, token al secondo e MB della KV cache. La cache cresce a gradini: ogni 256 token MLX aggiunge un blocco (circa 38 MB). I token al secondo scendono piano, perché a ogni passo l'attenzione legge una cache più lunga.
- **Sezione "Parallel prompts".** Quattro domande, prima una dopo l'altra, poi tutte insieme con `batch_generate`. Confronti i due tempi.

Nella sezione "Setup" c'è una cella con `# KVCache.step = 32`. MLX fa crescere la cache a blocchi di 256 token: per questo nella sezione "Prefill" vedi più token di quelli usati. Vuoi blocchi da 32 token? Togli il `#`, riavvia il kernel ed esegui le celle dall'inizio.

## Se qualcosa non funziona

| Problema | Cosa fare |
| --- | --- |
| `uv: command not found` | Esegui `brew install uv`. Poi apri un nuovo terminale. |
| Il primo avvio sembra bloccato | Aspetta. Il terminale o il notebook stanno scaricando file grandi. |
| Errore quando importi `mlx` | Il tuo Mac non ha Apple Silicon. Questo progetto non funziona su quel Mac. |
| Il download del modello è lento o si ferma | Esegui di nuovo la cella con `load(...)`. Il download riparte da dove si è fermato. Oppure scarica il modello a mano (vedi "Il modello"). |
| Una cella di streaming dura troppo | Premi il pulsante **Interrupt** (il quadrato) in alto nel notebook. Poi vai alla sezione dopo. |
| Poca memoria / il Mac rallenta | Chiudi le altre app. Riavvia il kernel ed esegui le celle dall'inizio. |
| Altri errori | Riavvia il kernel (menu **Kernel > Restart Kernel**) ed esegui le celle dall'inizio. |

## Per chi vuole sapere di più

- Le librerie e le loro versioni sono in `pyproject.toml` e `uv.lock`. Non modificare `uv.lock` a mano.
- `mlx-community/Qwen3-4B-4bit` è la conversione MLX a 4 bit di `Qwen/Qwen3-4B` (licenza Apache-2.0).
- I tempi dipendono dal tuo Mac. Il confronto tra le due misure resta uguale.

## Per approfondire

- [Attention Is All You Need](https://arxiv.org/pdf/1706.03762) (Vaswani et al., 2017): il paper del Transformer. Spiega query, chiavi e valori, cioè la "K" e la "V" della KV cache.
- [Visualizzazione interattiva](https://claude.ai/artifact/SdMfXgAoqrDHBCRPuSfk6y), fatta con Claude.
