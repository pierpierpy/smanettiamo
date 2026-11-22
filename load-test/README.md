# load-test

Quante persone può servire un Mac che esegue un modello di linguaggio, tutte insieme? In questo progetto facciamo un **load test**: mandiamo al modello 1, 2, 4, 8, 10 e 16 richieste in parallelo e misuriamo cosa cambia per ogni utente.

Il modello è [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) in 4 bit ([`mlx-community/Qwen3-4B-4bit`](https://huggingface.co/mlx-community/Qwen3-4B-4bit)), servito da `mlx_lm.server`. Il carico lo genera `aiperf` (lo strumento di benchmark di NVIDIA), da un altro computer.

## Cosa misura

- **TTFT** (*time to first token*): quanto aspetti prima di vedere il primo token della risposta. È il tempo del prefill. Qui lo diamo in secondi, al **p90**: il 90% delle richieste è più veloce di questo valore.
- **ITL** (*inter-token latency*): il tempo tra un token e il successivo. È il decode. Qui lo diamo in millisecondi, al p90.
- **Token al secondo per utente**: quanto veloce scrive la risposta chi sta usando il modello. Qui è la **mediana** (p50).

## Cosa trovi

- `load-test.ipynb`: il notebook di analisi. Legge `artifacts/riepilogo.csv` e mostra le tabelle.
- `artifacts/`: la **serie del 14 novembre**, quella che il notebook analizza. Prompt da 200 a 4000 token, il 4B e il 1,7B, sul Mac mini M2. `riepilogo.csv` la riassume, e `artifacts/orin/` contiene i risultati grezzi di aiperf (la cartella si chiama `orin` perché il carico partiva da lì).
- `artifacts-video/`: le **prove rifatte in diretta nel video**, con gli stessi comandi che trovi sotto. Prompt da 200 token, concorrenze 1, 2, 4, 8, 10 e 16 sul Mac mini M2, e concorrenze 1 e 10 sul Mac mini M5 Pro (cartelle `m5-...`).

Ogni prova ha la sua cartella, con il nome `<modello>-isl<token del prompt>-c<utenti>`. Dentro trovi i risultati di aiperf: `profile_export_aiperf.json` e `.csv` (le metriche), `profile_export.jsonl` (una riga per richiesta), `profile_export_console.txt` (la tabella che vedi nel terminale), `inputs.json`, `logs/` e `phases/` (warmup e misura).

Nei file ho sostituito il nome del computer con `<mac>`, il tuo utente con `<utente>` e un indirizzo della rete locale con `<ip-lan>`. I numeri non sono cambiati.

## Prima di iniziare

Per guardare il notebook ti servono:

- `uv` e `git` (`brew install uv git`);
- internet e circa 700 MB di spazio libero per l'ambiente. Il notebook legge solo i risultati: non scarica il modello.

Per rifare le misure servono anche un Mac con Apple Silicon (il server), un secondo computer da cui lanciare aiperf e circa 3 GB per il modello.

## Passo per passo (notebook)

1. Scarica la repo ed entra nella cartella:

   ```bash
   git clone https://github.com/pierpierpy/smanettiamo
   cd smanettiamo/load-test
   ```

2. Avvia JupyterLab:

   ```bash
   uv run jupyter lab
   ```

   Il primo avvio dura qualche minuto: `uv` installa Python 3.12 e le librerie. Il browser si apre da solo.

3. Apri `load-test.ipynb` ed esegui le celle in ordine con `Shift + Invio`.

4. Alla fine premi `Ctrl + C` due volte nel terminale.

## Rifare le misure

Scarica il modello una volta sola, prima di avviare il server:

```bash
uv run hf download mlx-community/Qwen3-4B-4bit
```

**Server**, sul Mac che serve il modello (`<mac>` è il suo nome o il suo indirizzo):

```bash
HF_HUB_OFFLINE=1 uv run mlx_lm.server \
  --model mlx-community/Qwen3-4B-4bit \
  --host "$(tailscale ip -4)" --port 8080 \
  --chat-template-args '{"enable_thinking":false}' \
  --prompt-cache-bytes 1000000000
```

Il server ascolta solo sull'indirizzo Tailscale. Se non usi Tailscale, metti `127.0.0.1` e lancia aiperf dallo stesso Mac.

**Una prova**, dal computer che genera il carico. aiperf (versione 0.13.0) è installato con `uv` in un progetto a parte (`uv add aiperf`):

```bash
uv run aiperf profile \
  --model mlx-community/Qwen3-4B-4bit \
  --url http://<mac>:8080 \
  --endpoint-type chat --streaming \
  --concurrency 1 --request-count 10 --warmup-request-count 1 \
  --synthetic-input-tokens-mean 200 --output-tokens-mean 100 \
  --artifact-dir artifacts-video/4b-isl200-c1
```

Ogni richiesta ha un prompt di circa 200 token e una risposta di circa 100. La prima richiesta è un warmup e non conta nei risultati.

**Il ciclo sulle concorrenze**, 1, 2, 4, 8, 10 e 16:

```bash
for c in 1 2 4 8 10 16; do
  uv run aiperf profile \
    --model mlx-community/Qwen3-4B-4bit \
    --url http://<mac>:8080 \
    --endpoint-type chat --streaming \
    --concurrency $c --request-count $(( c*4 > 10 ? c*4 : 10 )) --warmup-request-count 1 \
    --synthetic-input-tokens-mean 200 --output-tokens-mean 100 \
    --artifact-dir artifacts-video/4b-isl200-c$c
done
```

Le richieste non sono sempre 10: sono il massimo tra 10 e 4 volte la concorrenza (10, 10, 16, 32, 40, 64).

Sul Mac mini M5 Pro i comandi sono gli stessi, con `--artifact-dir artifacts-video/m5-4b-isl200-c1` (concorrenza 1, 10 richieste) e `artifacts-video/m5-4b-isl200-c10` (concorrenza 10, 40 richieste).

Quando hai finito, ferma il server con `Ctrl + C`.

## I numeri delle prove del video

Calcolati dai file in `artifacts-video/` (fase di misura, warmup escluso). Una prova per ogni configurazione, nessuna richiesta fallita.

**Mac mini M2**

| Utenti | Richieste | TTFT p90 (s) | ITL p90 (ms) | Token/s per utente |
|---:|---:|---:|---:|---:|
| 1 | 10 | 1,01 | 30,0 | 33,4 |
| 2 | 10 | 2,74 | 43,6 | 23,0 |
| 4 | 16 | 4,53 | 83,0 | 12,1 |
| 8 | 32 | 12,03 | 207,3 | 5,6 |
| 10 | 40 | 16,28 | 168,6 | 6,0 |
| 16 | 64 | 22,92 | 247,2 | 5,5 |

**Mac mini M5 Pro**

| Utenti | Richieste | TTFT p90 (s) | ITL p90 (ms) | Token/s per utente |
|---:|---:|---:|---:|---:|
| 1 | 10 | 0,17 | 11,3 | 90,9 |
| 10 | 40 | 1,04 | 31,2 | 33,1 |

Due note sui numeri:

- `artifacts/riepilogo.csv` calcola il p90 dai singoli record, con un metodo diverso da quello di aiperf. Di solito i due valori differiscono di circa l'1-2% o meno. A 1 utente, con sole 10 richieste, la differenza può essere più grande: per esempio l'ITL del 4B con prompt da 200 token è 30,6 ms in aiperf e 35,6 ms nel CSV. Le tabelle qui sopra usano i valori di aiperf.
- Ogni prova ha poche richieste (da 10 a 64), quindi rifacendo la misura i numeri cambiano, a volte parecchio. Per esempio l'ITL p90 sul Mac mini M2 è 159,7 ms a 8 utenti nella serie del 14 novembre e 207,3 ms in quella del video. A 10 utenti i due valori sono quasi uguali: 167,3 e 168,6 ms.

## Licenze

Il codice di questa repo usa la licenza MIT (vedi `LICENSE`). Il modello Qwen ha la sua licenza su Hugging Face: leggila prima di usarlo per altro.
