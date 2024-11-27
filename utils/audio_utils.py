from pydub import AudioSegment

def convert_aac_to_wav(input_path, output_path):
    """
    Converts an AAC audio file to WAV format.
    
    Args:
        input_path (str): Path to the input AAC file.
        output_path (str): Path to save the converted WAV file.
        
    Returns:
        None
    """
    try:
        audio = AudioSegment.from_file(input_path, format="aac")
        audio.export(output_path, format="wav")
    except Exception as e:
        raise RuntimeError(f"Error converting AAC to WAV: {e}")
