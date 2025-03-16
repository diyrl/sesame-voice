"""
Voice presets for CSM Speech Generator

This module contains basic voice types that can be used with the CSM model.
The interface is designed to provide a simple male/female option with full customization.
"""

class VoicePreset:
    """A preset configuration for a voice"""
    def __init__(self, 
                 name: str, 
                 speaker_id: int, 
                 temperature: float, 
                 min_p: float,
                 description: str):
        self.name = name
        self.speaker_id = speaker_id
        self.temperature = temperature
        self.min_p = min_p
        self.description = description
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "speaker_id": self.speaker_id,
            "temperature": self.temperature,
            "min_p": self.min_p,
            "description": self.description
        }

# Just two basic voice types as starting points
BASIC_VOICES = [
    VoicePreset("Male Voice", 2, 0.7, 0.05, "Natural male voice - customize the parameters below"),
    VoicePreset("Female Voice", 4, 0.7, 0.05, "Natural female voice - customize the parameters below"),
]

# Get a voice preset by name
def get_preset_by_name(name: str) -> VoicePreset:
    """Get a voice preset by its name"""
    for voice in BASIC_VOICES:
        if voice.name == name:
            return voice
    # Default to male voice if not found
    return BASIC_VOICES[0]

# Get voice presets by category
def get_presets_by_category():
    """Get voice presets organized by category"""
    return {
        "Voice Type": BASIC_VOICES,
    }