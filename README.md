# UnaLinea

**UnaLinea** è un'applicazione Python minimale pensata per aggiungere testo in
modo rapido e discreto a documenti Google Docs senza aprire il documento vero
e proprio. L'interfaccia grafica è volutamente essenziale e si limita a pochi
campi e pulsanti per ridurre al massimo l'ingombro sullo schermo.

Il progetto è stato sviluppato in modalità *vibe coded*: la logica iniziale è
nata da un prompt di intelligenza artificiale (salvato in `prompt.txt`) e poi
modificata a mano per adattarla alle esigenze specifiche.

## Caratteristiche principali

- Autenticazione con account Google tramite OAuth2 (desktop flow).
- Visualizzazione dell'elenco dei documenti Google Docs accessibili.
- Selezione di un documento su cui lavorare oppure creazione di un nuovo
documento via popup.
- Inserimento di testo aggiuntivo in coda al documento selezionato; ogni
elemento viene aggiunto su una nuova linea.
- Indicazione dell'ultima modifica con data e ora formattata in italiano
  (`gg/mm/aaaa alle hh:mm`).
- Pulsanti disabilitati e stato `Attendi...` durante le operazioni di salvataggio
  per evitare clic successivi.
- Popup di creazione documenti con placeholder e layout coerente all'app.
- Applicazione completamente in italiano.

> Nota: il contenuto dei documenti non viene mai mostrato dall'app; lo scopo è
> solo *appendere* testo.

## Requisiti

1. **Python 3.7+** con Tkinter incluso (di solito nelle distribuzioni standard).
2. Ambiente virtuale Python (consigliato).
3. Librerie Python installate:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 \
       google-api-python-client
   ```
4. Un file `credentials.json` generato nella Google Cloud Console per un client
   OAuth di tipo *Desktop application*. Questo file **non deve** essere pubblicato
   e va inserito nella directory principale del progetto.
5. Non pubblicare né `credentials.json` né `token.pickle` (vanno aggiunti a
   `.gitignore`).

## Installazione e avvio

```bash
# clonare il repository
git clone <url-del-repo>
cd UnaLinea

# creare e attivare venv
python -m venv venv
venv\Scripts\activate.ps1    # Windows PowerShell
# oppure: source venv/bin/activate   # Unix

# installare dipendenze
pip install -r requirements.txt   # oppure i pacchetti sopra

# copiare credentials.json nella cartella del progetto

# eseguire
python unalinea.py
```

Alla prima esecuzione, l'app tenterà di aprire il browser per chiedere
l'autorizzazione all'accesso Google; dopo il consenso genererà un file
`token.pickle` per memorizzare il token di accesso.

## Uso

1. Avvia l'app (`python unalinea.py`).
2. Se non è già loggato, si aprirà un browser per autorizzare l'accesso.
3. La combobox verrà popolata con i documenti Google Docs modificabili; l'ultima
   voce è **"Nuovo documento..."** per crearne uno nuovo.
4. Seleziona un documento e digita una riga di testo; premi **Salva**.
5. L'etichetta in basso mostrerà la data/ora dell'ultima modifica.
6. Usa il pulsante **Esci** per disconnetterti.

### Creazione documento

- Se scegli "Nuovo documento..." si apre un popup con un campo di testo.
- Inserisci il titolo (placeholder "Titolo documento") e premi **Crea** o
  **Annulla**.
- Il nuovo documento sarà selezionato automaticamente e disponibile per
  l'editing.

## Struttura del progetto

- `unalinea.py` – codice principale dell'applicazione.
- `prompt.txt` – prompt originale usato per generare il codice con AI.
- `requirements.txt` – elenco pacchetti richiesti (se presente).
- `.gitignore` – file per escludere venv, credenziali, token, ecc.

## Note per il repository GitHub

- Assicurati che **non siano tracciati** i file sensibili (`credentials.json`,
  `token.pickle`) e l'ambiente virtuale.
- Il README spiega il funzionamento e dà istruzioni di installazione.
- Aggiungi una licenza adeguata (`LICENSE`) prima di pubblicare.

> Il file `prompt.txt` include il prompt originale: tienilo visibile per chi
> voglia comprendere la genesi del progetto.

## Futuri sviluppi

- Aggiungere funzionalità di visualizzazione o modifica del contenuto.
- Implementare versioning automatico delle modifiche.
- Integrare la gestione di più account o un'interfaccia web.

---

Applicazione scritta in italiano; pensata per un utilizzo rapido e minimale.
Buon coding! (vibe coded 💡)