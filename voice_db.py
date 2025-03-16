"""
Voice Preset Database - SQLite implementation for CSM-MLX
"""

import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class VoicePreset:
    """Voice preset data class"""
    name: str
    speaker_id: int
    temperature: float
    min_p: float
    seed: str = None
    speed: float = 1.0
    id: int = None
    created_at: str = None
    description: str = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "speaker_id": self.speaker_id,
            "temperature": self.temperature,
            "min_p": self.min_p,
            "seed": self.seed,
            "speed": self.speed,
            "created_at": self.created_at,
            "description": self.description
        }

class VoicePresetDB:
    """SQLite database for voice presets"""
    
    def __init__(self, db_path="voice_presets.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create voice_presets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            speaker_id INTEGER NOT NULL,
            temperature REAL NOT NULL,
            min_p REAL NOT NULL,
            seed TEXT,
            speed REAL DEFAULT 1.0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create voice_samples table to store sample audio for presets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER NOT NULL,
            audio_path TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (preset_id) REFERENCES voice_presets (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_preset_by_id(self, preset_id):
        """Get a single preset by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM voice_presets WHERE id = ?', (preset_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        preset = VoicePreset(
            id=row['id'],
            name=row['name'],
            speaker_id=row['speaker_id'],
            temperature=row['temperature'],
            min_p=row['min_p'],
            seed=row['seed'],
            speed=row['speed'],
            description=row['description'],
            created_at=row['created_at']
        )
        
        conn.close()
        return preset
    
    def get_all_presets(self):
        """Get all voice presets"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM voice_presets ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        presets = []
        for row in rows:
            preset = VoicePreset(
                id=row['id'],
                name=row['name'],
                speaker_id=row['speaker_id'],
                temperature=row['temperature'],
                min_p=row['min_p'],
                seed=row['seed'],
                speed=row['speed'],
                description=row['description'],
                created_at=row['created_at']
            )
            presets.append(preset)
        
        conn.close()
        return presets
    
    def create_preset(self, preset):
        """Create a new voice preset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO voice_presets (name, speaker_id, temperature, min_p, seed, speed, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            preset.name,
            preset.speaker_id,
            preset.temperature,
            preset.min_p,
            preset.seed,
            preset.speed,
            preset.description
        ))
        
        preset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return preset_id
    
    def update_preset(self, preset):
        """Update an existing preset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE voice_presets 
        SET name = ?, speaker_id = ?, temperature = ?, min_p = ?, seed = ?, speed = ?, description = ?
        WHERE id = ?
        ''', (
            preset.name,
            preset.speaker_id,
            preset.temperature,
            preset.min_p,
            preset.seed,
            preset.speed,
            preset.description,
            preset.id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_preset(self, preset_id):
        """Delete a preset by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Also delete related voice samples (cascade)
        cursor.execute('DELETE FROM voice_presets WHERE id = ?', (preset_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def add_voice_sample(self, preset_id, audio_path, text):
        """Add a sample audio for a voice preset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO voice_samples (preset_id, audio_path, text)
        VALUES (?, ?, ?)
        ''', (preset_id, audio_path, text))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return sample_id
    
    def get_voice_samples(self, preset_id):
        """Get all voice samples for a preset"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM voice_samples 
        WHERE preset_id = ?
        ORDER BY created_at DESC
        ''', (preset_id,))
        
        samples = []
        for row in cursor.fetchall():
            sample = {
                'id': row['id'],
                'preset_id': row['preset_id'],
                'audio_path': row['audio_path'],
                'text': row['text'],
                'created_at': row['created_at']
            }
            samples.append(sample)
        
        conn.close()
        return samples
    
    def find_similar_preset(self, speaker_id, temperature, min_p, seed=None):
        """Find presets with similar settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Adjust temperature and min_p ranges for similarity
        temp_min = float(temperature) - 0.05
        temp_max = float(temperature) + 0.05
        minp_min = float(min_p) - 0.02
        minp_max = float(min_p) + 0.02
        
        # Query for similar presets
        if seed:
            # If seed is provided, it must match exactly
            cursor.execute('''
            SELECT * FROM voice_presets 
            WHERE speaker_id = ?
            AND temperature BETWEEN ? AND ?
            AND min_p BETWEEN ? AND ?
            AND seed = ?
            ORDER BY created_at DESC
            ''', (speaker_id, temp_min, temp_max, minp_min, minp_max, seed))
        else:
            # If no seed, match by other parameters
            cursor.execute('''
            SELECT * FROM voice_presets 
            WHERE speaker_id = ?
            AND temperature BETWEEN ? AND ?
            AND min_p BETWEEN ? AND ?
            ORDER BY created_at DESC
            ''', (speaker_id, temp_min, temp_max, minp_min, minp_max))
        
        presets = []
        for row in cursor.fetchall():
            preset = VoicePreset(
                id=row['id'],
                name=row['name'],
                speaker_id=row['speaker_id'],
                temperature=row['temperature'],
                min_p=row['min_p'],
                seed=row['seed'],
                speed=row['speed'],
                description=row['description'],
                created_at=row['created_at']
            )
            presets.append(preset)
        
        conn.close()
        return presets

# Create a singleton instance
db = VoicePresetDB()