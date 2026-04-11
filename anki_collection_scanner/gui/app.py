import tkinter as tk
import queue
import threading
import time

from tkinter import ttk
from typing import Dict, Optional  # Optional kept for shutdown_thread type hint

from anki_collection_scanner.main import sync_on_startup, sync_manual, sync_on_shutdown
from anki_collection_scanner.application.field_config import FieldConfig
from anki_collection_scanner.domain.result import Result
from anki_collection_scanner.application.usecases.add_audio_to_deck import AudioOperationReport, AddAudioError
from anki_collection_scanner.domain.collection_snapshot.collection_snapshot import CollectionSnapshot
from anki_collection_scanner.application.usecases.sync_collection import SyncCollectionUseCase
from anki_collection_scanner.application.usecases.add_audio_to_deck import AddAudioToDeckUseCase
from anki_collection_scanner.infrastructure.field_config_repository import FieldConfigRepository

class App:
    def __init__(self, app_dependencies: dict):
        self.sync_use_case: SyncCollectionUseCase  = app_dependencies["sync_collection_use_case"]
        self.audio_use_case: AddAudioToDeckUseCase = app_dependencies["audio_use_case"]
        self.field_config_repo: FieldConfigRepository = app_dependencies["field_config_repository"]
        self.snapshot: CollectionSnapshot = CollectionSnapshot() #set after executing sync on a thread
        self._saved_fields_config: Dict[str, FieldConfig] = self.field_config_repo.load()
        self.result_queue = queue.Queue()
        self.shutdown_thread: Optional[threading.Thread] = None
        self._close_requested_at: float = 0.0
        self.root = tk.Tk()
        self._build_ui()
        #self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.status_label = ttk.Label(self.root, text="Syncing")
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.deck_combobox = ttk.Combobox(self.root, values = [], state="disabled")
        self.deck_combobox.set("Select Deck")
        self.deck_combobox.bind("<<ComboboxSelected>>", self._on_deck_selected)
        self.deck_combobox.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.fields_frame = ttk.LabelFrame(self.root, text="Field Configuration")
        self.fields_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Label(self.fields_frame, text="(fields will appear here)").grid(row=0, column=0, padx=5, pady=5)

        self.sync_btn = ttk.Button(self.root, text="Sync collection", command=self._start_manual_sync, state="disabled")
        self.sync_btn.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.execute_btn = ttk.Button(self.root, text="Execute operation", state="disabled", command=self._on_execute)
        self.execute_btn.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.result_label = ttk.Label(self.root, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.field_combos: Dict[str, Dict[str, ttk.Combobox]] = {}

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)


    def run(self):
        self._start_manual_sync()
        self.root.after(100, self._poll_queue)
        self.root.mainloop()

    def _poll_queue(self):
        try:
            while True:
                tag, result = self.result_queue.get_nowait()
                if tag == "startup_sync":
                    self._handle_startup_sync(result)
                elif tag == "manual_sync":
                    self._handle_manual_sync(result)
                elif tag == "shutdown_sync":
                    pass
                elif tag == "deck_note_ids":
                    deck_name, note_ids = result
                    self._handle_deck_note_ids(deck_name, note_ids)
                elif tag == "audio_addition":
                    self._handle_audio_addition(result)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _start_startup_sync(self):
        def worker():
            result = sync_on_startup(self.sync_use_case)
            self.result_queue.put(("startup_sync", result))
        
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _handle_startup_sync(self, result):
        if not result["success"]:
            print("Sync failed")
            return
        print(f"Sync succeeded, returning snapshot..")
        self.snapshot = result["snapshot"]
    
    def _start_deck_note_ids_fetch(self, deck_name):
        def worker():
            self.deck_combobox
            note_ids = self.sync_use_case.fetch_deck_note_ids(deck_name)
            self.result_queue.put(("deck_note_ids", (deck_name, note_ids)))
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        
    def _handle_deck_note_ids(self, deck_name, note_ids):
        self.deck_combobox.config(state="readonly")
        model_names = {self.snapshot.notes[note_id].model for note_id in note_ids if note_id in self.snapshot.notes}
        models = [m for m in self.snapshot.models.values() if m.model_name in model_names]

        for row_num, model in enumerate(models, start=1):
            ttk.Label(self.fields_frame, text=model.model_name).grid(row=row_num, column=0, padx=5, pady=3, sticky="w")
            saved = self._saved_fields_config.get(model.model_name)

            primary_combo = ttk.Combobox(self.fields_frame, values=model.model_field_names, state="readonly")
            primary_combo.grid(row=row_num, column=1, padx=5)
    
            secondary_combo = ttk.Combobox(self.fields_frame, values=model.model_field_names, state="readonly")
            secondary_combo.grid(row=row_num, column=2, padx=5)
    
            audio_combo = ttk.Combobox(self.fields_frame, values=model.model_field_names, state="readonly")
            audio_combo.grid(row=row_num, column=3, padx=5)

            if saved:
                if saved.primary_field in model.model_field_names:
                    primary_combo.set(saved.primary_field)
                if saved.secondary_field in model.model_field_names:
                    secondary_combo.set(saved.secondary_field)
                if saved.audio_field in model.model_field_names:
                    audio_combo.set(saved.audio_field)

            self.field_combos[model.model_name] = {
                "primary": primary_combo,
                "secondary": secondary_combo,
                "audio": audio_combo,
            }

            for combo in (primary_combo, secondary_combo, audio_combo):
                combo.bind("<<ComboboxSelected>>", lambda e: self._check_execute_ready())
            self._check_execute_ready()

    def _start_manual_sync(self):
        def worker():
            result = sync_manual(self.sync_use_case)
            self.result_queue.put(("manual_sync", result))

        self.status_label["text"] = "Collection sync in progress..."
        self.sync_btn.config(state="disabled")
        self.deck_combobox.config(state="disabled")
        self.execute_btn.config(state="disabled")
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.field_combos = {}
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _handle_manual_sync(self, result):
        if not result["success"]:
            self.status_label["text"] = "Sync failed"
            self.sync_btn.config(state="normal")
            return
        self.snapshot = result["snapshot"]
        self.status_label["text"] = "Ready"
        self.deck_combobox["values"] = [d.deck_name for d in self.snapshot.decks.values()]
        self.deck_combobox.set("Select Deck")
        self.deck_combobox.config(state="readonly")
        self.sync_btn.config(state="normal")

    def _start_audio_addition(self, deck_name: str):
        self.execute_btn.config(state="disabled")
        self.sync_btn.config(state="disabled")
        self.result_label.config(text="Processing...")
        def worker():
            result = self.audio_use_case.add_audio_to_deck(deck_name, self.snapshot, self.fields_config)
            self.result_queue.put(("audio_addition", result))
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _handle_audio_addition(self, result: Result[AudioOperationReport, AddAudioError]):
        self.execute_btn.config(state="normal")
        self.sync_btn.config(state="normal")
        if result.is_err():
            error = result.unwrap_err()
            self.result_label.config(text=f"Error: {error}")
            return
        report = result.unwrap()
        self.field_config_repo.save(self.fields_config)
        self._saved_fields_config = self.fields_config
        self.result_label.config(text=report.summary())

    def _on_execute(self):
        deck_name = self.deck_combobox.get()
        self.fields_config = {
            model_name: FieldConfig(
                primary_field=combos["primary"].get(),
                secondary_field=combos["secondary"].get(),
                audio_field=combos["audio"].get(),
            )
            for model_name, combos in self.field_combos.items()
            if all(c.get() != "" for c in combos.values())
        }
        self._start_audio_addition(deck_name)

    def _check_execute_ready(self):
        if not self.field_combos:
            self.execute_btn.config(state="disabled")
            return
        any_complete = any(
            all(combo.get() != "" for combo in combos.values())
            for combos in self.field_combos.values()
        )
        self.execute_btn.config(state="normal" if any_complete else "disabled")

    def _on_deck_selected(self, event):
        deck = self.deck_combobox.get()
        self.result_label.config(text=f"Selected deck: {deck}")

        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        self.field_combos = {}
        self.execute_btn.config(state="disabled")

        ttk.Label(self.fields_frame, text="Model",          font=("", 9, "bold")).grid(row=0, column=0, padx=5, pady=(5, 2), sticky="w")
        ttk.Label(self.fields_frame, text="Primary field",  font=("", 9, "bold")).grid(row=0, column=1, padx=5, pady=(5, 2))
        ttk.Label(self.fields_frame, text="Secondary field",font=("", 9, "bold")).grid(row=0, column=2, padx=5, pady=(5, 2))
        ttk.Label(self.fields_frame, text="Audio field",    font=("", 9, "bold")).grid(row=0, column=3, padx=5, pady=(5, 2))

        self._start_deck_note_ids_fetch(deck)
        self.deck_combobox.config(state="disabled")


    def _on_close(self):
        if self.shutdown_thread is None:
            self._close_requested_at = time.time()
            self.shutdown_thread = threading.Thread(
                target=sync_on_shutdown,
                args=(self.sync_use_case,),
                daemon=True,
            )
            self.shutdown_thread.start()
            print("Waiting for shutdown sync to finish before closing...")

        elapsed = time.time() - self._close_requested_at
        if self.shutdown_thread.is_alive() and elapsed < 10:
            self.root.after(100, self._on_close)
            return

        self.root.destroy()