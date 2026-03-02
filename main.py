#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applicazione Tkinter minimale per aggiungere testo a documenti Google.
Interfaccia in italiano come richiesto.

NOTE:
- Questa implementazione contiene funzioni "stub" che simulano il
  comportamento di autenticazione e delle API Google. Per un uso reale
  bisogna integrare le librerie google-auth, google-api-python-client e
  gestire le credenziali OAuth2.
- Lo scopo del progetto è mostrare la struttura dell'interfaccia
  e la logica dell'applicazione.
"""

import datetime
import os
import pickle
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# librerie Google
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ambiti richiesti: metadata drive per elenchi, modifica documenti per scrittura
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/documents'
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UnaLinea")
        # dimensioni compatte, altezza fissa
        self.geometry("600x120")
        # non permettiamo ridimensionamenti
        self.resizable(False, False)

        # stato dell'app
        self.logged_in = False
        self.documenti = []  # lista dei documenti disponibili (nomi)
        self.documenti_map = {}  # nome -> id
        self.documento_attivo = None
        self.documento_attivo_id = None
        self.drive_service = None
        self.docs_service = None

        self._crea_widgets()
        self._posiziona_widgets()
        self._aggiorna_layout()
        # proviamo l'accesso automatico se abbiamo già un token salvato
        self._auto_login()

    def _crea_widgets(self):
        # prima colonna
        self.combo_doc = ttk.Combobox(self, state="readonly")
        self.combo_doc['values'] = []
        self.combo_doc.current(0) if self.combo_doc['values'] else None
        self.entry_testo = ttk.Entry(self)
        self.label_info = ttk.Label(self, text="Nessun documento selezionato")

        # seconda colonna
        # impostiamo una larghezza fissa (numero di caratteri) per pulsanti
        self.btn_seleziona = ttk.Button(self, text="Seleziona", command=self.seleziona_documento, width=10)
        self.btn_salva = ttk.Button(self, text="Salva", command=self.salva_testo, width=10)
        self.btn_login = ttk.Button(self, text="Accedi", command=self.toggle_login, width=10)

    def _posiziona_widgets(self):
        # griglia 2x3
        # colonne: 0 espandibile, 1 dimensione fissa per i pulsanti
        self.columnconfigure(0, weight=1)
        # la colonna dei bottoni non si espande con la finestra
        self.columnconfigure(1, weight=0)

        # rendiamo le righe più compatte impostando una minsize ridotta
        # riduciamo ulteriormente i minsize per rendere le righe ancora più compatte
        self.rowconfigure(0, weight=1, minsize=20)
        self.rowconfigure(1, weight=1, minsize=20)
        self.rowconfigure(2, weight=1, minsize=20)

        # posizionamento
        self.combo_doc.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.entry_testo.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        # label non si espande in orizzontale, resta allineata a sinistra
        self.label_info.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.btn_seleziona.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.btn_salva.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.btn_login.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

    def _aggiorna_layout(self):
        # inizialmente disabilitiamo pulsanti che richiedono accesso
        self.btn_seleziona.config(state="disabled")
        self.btn_salva.config(state="disabled")
        self.combo_doc.config(state="disabled")

    # funzioni di gestione
    def toggle_login(self):
        if not self.logged_in:
            self._login_google()
        else:
            self._logout_google()

    def _login_google(self):
        # login OAuth reale
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # creiamo i servizi
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)

        self.logged_in = True
        self.btn_login.config(text="Esci")
        self.documenti = self._carica_documenti()  # recupera dai server
        self._aggiorna_combo()
        self.combo_doc.config(state="readonly")
        self.btn_seleziona.config(state="normal")
        # non mostriamo popup di conferma in avvio normale

    def _logout_google(self):
        self.logged_in = False
        self.btn_login.config(text="Accedi")
        self.documenti = []
        self.documento_attivo = None
        self.combo_doc.set("")
        self.combo_doc.config(state="disabled")
        self.btn_seleziona.config(state="disabled")
        self.btn_salva.config(state="disabled")
        self.label_info.config(text="Nessun documento selezionato")
        messagebox.showinfo("Logout", "Hai effettuato il logout.")

    def _carica_documenti(self):
        # reale: interroga Drive per ottenere i file Google Docs accessibili
        docs = []
        self.documenti_map.clear()
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.document' and trashed=false",
                fields="files(id,name)",
                pageSize=100
            ).execute()
            files = results.get('files', [])
            for f in files:
                name = f['name']
                docs.append(name)
                self.documenti_map[name] = f['id']
        except Exception as e:
            messagebox.showerror("Errore Drive", f"Impossibile caricare documenti: {e}")
        docs.append("Nuovo documento...")
        return docs

    def _aggiorna_combo(self):
        vals = self.documenti.copy()
        self.combo_doc['values'] = vals
        if vals:
            self.combo_doc.current(0)

    def seleziona_documento(self):
        if not self.logged_in:
            return
        scelta = self.combo_doc.get()
        if scelta == "Nuovo documento...":
            self._popup_nuovo_documento()
        else:
            self.documento_attivo = scelta
            self.documento_attivo_id = self.documenti_map.get(scelta)
            self.btn_salva.config(state="normal")
            self._aggiorna_label()
            # nessun popup al cambio documento

    def _auto_login(self):
        # se esiste token.pickle, carichiamo le credenziali e impostiamo lo stato
        if os.path.exists('token.pickle'):
            try:
                # chiamiamo la procedura di login, ma senza popup informativi
                self._login_google()
            except Exception as e:
                print(f"[INFO] auto-login fallito: {e}")

    def _popup_nuovo_documento(self):
        # pop-up personalizzato per creare un nuovo documento
        popup = tk.Toplevel(self)
        popup.title("Nuovo documento")
        # renderemo il pop-up alto quanto la finestra principale
        # assicuriamoci che la finestra principale abbia già dimensioni reali
        self.update_idletasks()
        main_h = self.winfo_height()
        popup.geometry(f"300x{main_h}")
        popup.resizable(False, False)

        lbl = ttk.Label(popup, text="Nome documento:")
        lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5,0))
        entry = ttk.Entry(popup)
        entry.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        popup.columnconfigure(0, weight=1)
        popup.columnconfigure(1, weight=1)
        # righe: 0=label, 1=entry, 2=bottoni
        # usiamo un minsize pari a un terzo dell'altezza della finestra principale
        min_riga = max(30, self.winfo_height() // 3)
        popup.rowconfigure(0, weight=0, minsize=min_riga)
        popup.rowconfigure(1, weight=1, minsize=min_riga)
        popup.rowconfigure(2, weight=0, minsize=min_riga)

        def cancella():
            popup.destroy()

        def crea():
            nome = entry.get().strip()
            if nome:
                doc_metadata = {'title': nome}
                try:
                    created = self.docs_service.documents().create(body=doc_metadata).execute()
                    doc_id = created.get('documentId')
                    self.documenti.insert(-1, nome)
                    self.documenti_map[nome] = doc_id
                    self._aggiorna_combo()
                    self.combo_doc.set(nome)
                    self.documento_attivo = nome
                    self.documento_attivo_id = doc_id
                    self.btn_salva.config(state="normal")
                    self._aggiorna_label()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Errore Docs", f"Impossibile creare documento: {e}")
            else:
                messagebox.showwarning("Attenzione", "Inserisci un nome valido.")

        btn_cancel = ttk.Button(popup, text="Annulla", command=cancella)
        btn_create = ttk.Button(popup, text="Crea", command=crea)
        btn_cancel.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        btn_create.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

    def salva_testo(self):
        if not self.documento_attivo:
            return
        testo = self.entry_testo.get()
        if testo.strip() == "":
            messagebox.showwarning("Attenzione", "Il campo di testo è vuoto.")
            return
        # disabilita pulsante e mostra stato di attesa
        self.btn_salva.config(text="Attendi...", state="disabled")
        try:
            self._aggiungi_testo_documento(self.documento_attivo, testo)
            ora = datetime.datetime.now().strftime("%d/%m/%Y alle %H:%M")
            self.label_info.config(text=f"Ultima modifica: {ora}")
            # nessun popup di conferma, il pulsante mostra lo stato
        finally:
            # ripristina pulsante
            self.btn_salva.config(text="Salva", state="normal")

    def _aggiungi_testo_documento(self, doc, testo):
        # inserisce testo alla fine del documento tramite Docs API
        doc_id = self.documento_attivo_id
        if not doc_id:
            print("[DEBUG] nessun ID documento, salto il salvataggio")
            return
        print(f"[DEBUG] salvataggio su doc_id={doc_id}, testo='{testo}'")
        try:
            # recupera il documento per sapere l'indice di fine
            document = self.docs_service.documents().get(documentId=doc_id).execute()
            content = document.get('body', {}).get('content', [])
            end_index = 1
            if content:
                last = content[-1]
                # l'indice finale restituito è esclusivo; occorre inserire prima di tale
                # fine (endIndex-1) per evitare l'errore visto in precedenza.
                end_index = (last.get('endIndex', 1) or 1) - 1
            # se il documento contiene già testo, inseriamo un caporiga
            text_to_insert = testo
            if end_index > 1:
                text_to_insert = "\n" + testo
            requests = [
                {
                    'insertText': {
                        'location': {'index': end_index},
                        'text': text_to_insert
                    }
                }
            ]
            self.docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        except Exception as e:
            # mostriamo più contesto e logghiamo in console
            msg = f"Impossibile salvare testo (doc_id={doc_id}): {e}"
            print("[ERROR]", msg)
            messagebox.showerror("Errore Docs", msg)

    def _aggiorna_label(self):
        if self.documento_attivo:
            self.label_info.config(text=f"Documento attivo: {self.documento_attivo}")
        else:
            self.label_info.config(text="Nessun documento selezionato")


if __name__ == "__main__":
    app = App()
    app.mainloop()