"""Dialog for taking snapshots"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QRadioButton, QButtonGroup,
    QPushButton, QDialogButtonBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from typing import Optional, List
from src.models.session_definition import SessionDefinition
from src.models.snapshot import Snapshot
from src.application.snapshot_manager import SnapshotManager
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SnapshotDialog(QDialog):
    """Dialog for taking a snapshot"""
    
    def __init__(
        self,
        parent=None,
        snapshot_manager: Optional[SnapshotManager] = None,
        current_session: Optional[SessionDefinition] = None,
        all_sessions: Optional[List[SessionDefinition]] = None
    ):
        """Initialize snapshot dialog"""
        super().__init__(parent)
        self.setWindowTitle("Take Snapshot")
        self.setMinimumSize(500, 300)
        
        self.snapshot_manager = snapshot_manager
        self.current_session = current_session
        self.all_sessions = all_sessions or []
        self.snapshot: Optional[Snapshot] = None
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Scope selection
        scope_group = QGroupBox("Scope")
        scope_layout = QVBoxLayout()
        
        self.scope_group = QButtonGroup(self)
        
        if self.current_session:
            self.current_session_radio = QRadioButton(f"Current Session: {self.current_session.name}")
            self.current_session_radio.setChecked(True)
            self.scope_group.addButton(self.current_session_radio, 0)
            scope_layout.addWidget(self.current_session_radio)
        
        if self.all_sessions:
            self.all_sessions_radio = QRadioButton(f"All Sessions ({len(self.all_sessions)} sessions)")
            if not self.current_session:
                self.all_sessions_radio.setChecked(True)
            self.scope_group.addButton(self.all_sessions_radio, 1)
            scope_layout.addWidget(self.all_sessions_radio)
        
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)
        
        # Snapshot info
        info_group = QGroupBox("Snapshot Information")
        form = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        default_name = f"Snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name_edit.setText(default_name)
        form.addRow("Navn:", self.name_edit)
        
        # Note
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Noter om denne snapshot (valgfrit)...")
        self.note_edit.setMaximumHeight(100)
        form.addRow("Note:", self.note_edit)
        
        info_group.setLayout(form)
        layout.addWidget(info_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._take_snapshot)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _take_snapshot(self):
        """Take snapshot"""
        if not self.snapshot_manager:
            QMessageBox.warning(self, "Error", "Snapshot manager ikke tilgængelig.")
            return
        
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validering", "Snapshot navn er påkrævet.")
            return
        
        note = self.note_edit.toPlainText().strip() or None
        
        try:
            # Check which radio button is selected - prioritize all_sessions_radio if both exist
            use_all_sessions = False
            
            if hasattr(self, 'all_sessions_radio') and self.all_sessions_radio.isChecked():
                use_all_sessions = True
            elif hasattr(self, 'current_session_radio') and self.current_session_radio.isChecked() and self.current_session:
                use_all_sessions = False
            else:
                # Fallback: if no clear selection, default to all sessions if available
                use_all_sessions = bool(self.all_sessions)
            
            if use_all_sessions:
                # Take snapshot of all sessions
                if not self.all_sessions:
                    QMessageBox.warning(self, "Ingen sessions", "Ingen sessions tilgængelig.")
                    return
                
                logger.info(f"Taking snapshot of all {len(self.all_sessions)} sessions")
                self.snapshot = self.snapshot_manager.take_snapshot_from_all_sessions(
                    self.all_sessions,
                    snapshot_name=name,
                    note=note
                )
            else:
                # Take snapshot of current session only
                if not self.current_session:
                    QMessageBox.warning(self, "Ingen session", "Ingen aktive session valgt.")
                    return
                
                logger.info(f"Taking snapshot of current session: {self.current_session.name}")
                self.snapshot = self.snapshot_manager.take_snapshot_from_session(
                    self.current_session,
                    snapshot_name=name,
                    note=note
                )
                if not self.snapshot:
                    QMessageBox.warning(
                        self,
                        "Ingen data",
                        f"Ingen poll data tilgængelig for session '{self.current_session.name}'. Start session først."
                    )
                    return
            
            if self.snapshot:
                message = f"Snapshot '{name}' oprettet med {self.snapshot.get_value_count()} værdier fra {len(self.snapshot.sessions)} session(s)."
                if use_all_sessions and len(self.snapshot.sessions) < len(self.all_sessions):
                    message += f"\n\nBemærk: {len(self.all_sessions) - len(self.snapshot.sessions)} session(s) blev sprunget over fordi de ikke har poll data. Start alle sessions først for at inkludere dem."
                
                QMessageBox.information(
                    self,
                    "Success",
                    message
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Kunne ikke oprette snapshot.")
        
        except Exception as e:
            logger.error(f"Error taking snapshot: {e}")
            QMessageBox.warning(self, "Error", f"Fejl ved oprettelse af snapshot: {e}")
    
    def get_snapshot(self) -> Optional[Snapshot]:
        """Get created snapshot"""
        return self.snapshot
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

