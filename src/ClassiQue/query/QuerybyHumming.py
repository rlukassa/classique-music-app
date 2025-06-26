import mido
import numpy as np
import json
import os
import time

# Bagian Pemrosesan Audio 
def readMIDI(filename):
    """Membaca file MIDI dan mengekstrak catatan melodi."""
    try:
        thisMidi = mido.MidiFile(filename)
        melodyNotes = []
        for track in thisMidi.tracks:
            for message in track:
                if message.type == 'note_on' and message.velocity > 0:
                    melodyNotes.append(message.note)
        return np.array(melodyNotes)
    except Exception as e:
        print(f"Error reading MIDI file {filename}: {e}")
        return np.array([])

# Fungsi Windowing
def windowing(melodyNotes, windowSize=30, slidingStep=6):
    """Membagi urutan nada menjadi jendela-jendela kecil."""
    windows = []
    for i in range(0, len(melodyNotes) - windowSize + 1, slidingStep):
        window = melodyNotes[i:i + windowSize]
        windows.append(window)
    return windows

# Normalisasi Tempo dan Pitch
def normalizeTempoPitch(notes):
    """Normalisasi pitch dengan mean dan standar deviasi."""
    if len(notes) == 0:
        return notes
    pitchMean = np.mean(notes)
    pitchStd = np.std(notes)
    return (notes - pitchMean) / pitchStd if pitchStd != 0 else notes

# Ekstraksi Fitur
def extractATB(melodyNotes):
    """Ekstraksi fitur ATB (Absolute Tone Bar)."""
    hist = np.zeros(128)  # Histogram untuk 128 nada MIDI
    for note in melodyNotes:
        hist[int(note)] += 1
    return hist

def extractRTB(melodyNotes):
    """Ekstraksi fitur RTB (Relative Tone Bar)."""
    hist = np.zeros(255)  # Histogram untuk interval nada dari -127 hingga +127
    for i in range(1, len(melodyNotes)):
        diff = int(melodyNotes[i] - melodyNotes[i - 1])
        if -127 <= diff <= 127:
            hist[diff + 127] += 1
    return hist 

def extractFTB(melodyNotes):
    """Ekstraksi fitur FTB (First Tone Bar)."""
    hist = np.zeros(255)  # Histogram untuk perbedaan dengan nada pertama
    firstNote = melodyNotes[0]
    for note in melodyNotes:
        diff = int(note - firstNote)
        hist[diff + 127] += 1
    return hist

def loadMapper(mapper, search_path='./uploads'):
    """Memuat metadata mapper dari file JSON yang terletak di search_path."""
    # Menentukan path lengkap ke file mapper
    mapper_path = os.path.join(search_path, mapper)
    
    # Memeriksa apakah file JSON ada di direktori yang ditentukan
    if os.path.exists(mapper_path):
        with open(mapper_path, 'r') as f:
            return json.load(f)
    else:
        print(f"File {mapper} tidak ditemukan di {search_path}.")
        return None


# Normalisasi Histogram
def normalizeHistogram(hist):
    """Normalisasi histogram."""
    total = np.sum(hist)
    if total == 0:
        return hist  # Jika totalnya 0, tidak perlu normalisasi
    return hist / total

# Cosine Similarity
def cosineSimilarity(vec1, vec2):
    """Menghitung cosine similarity antara dua vektor."""
    dotProduct = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:  # Cek jika ada vektor dengan panjang 0
        return 0
    similarity = dotProduct / (norm1 * norm2)
    return min(max(similarity, -1), 1)

# Fungsi untuk query humming
def querybyHumming(hummingMIDI, datasetPath, mapper, uploadFolder=None):
    """Melakukan pencocokan berdasarkan humming MIDI."""
    print("Membaca file humming MIDI...")
    hummingNotes = readMIDI(hummingMIDI)
    if hummingNotes.size == 0:
        print("Tidak ada catatan melodi pada file humming.")
        return []
    
    print("Normalisasi tempo dan pitch...")
    hummingNotes = normalizeTempoPitch(hummingNotes)  
    
    # Ekstraksi fitur global (ATB, RTB, FTB)
    hummingATB = extractATB(hummingNotes)
    normalizehummingATB = normalizeHistogram(hummingATB)
    
    hummingRTB = extractRTB(hummingNotes)
    normalizehummingRTB = normalizeHistogram(hummingRTB)
    
    hummingFTB = extractFTB(hummingNotes)
    normalizehummingFTB = normalizeHistogram(hummingFTB)   
    
    # Windowing
    windowedHumming = windowing(hummingNotes, windowSize=30, slidingStep=6)
    
    # Similarity untuk setiap window
    windowSimilarity = []
    for window in windowedHumming:
        windowNotes = normalizeTempoPitch(np.array(window))
        
        windowATB = extractATB(windowNotes)
        normalizeWindowATB = normalizeHistogram(windowATB)
        
        windowRTB = extractRTB(windowNotes)
        normalizeWindowRTB = normalizeHistogram(windowRTB)
        
        windowFTB = extractFTB(windowNotes)
        normalizeWindowFTB = normalizeHistogram(windowFTB)
        
        # Cosine Similarity untuk setiap fitur window
        windowSimilarityATB = cosineSimilarity(normalizehummingATB, normalizeWindowATB)
        windowSimilarityRTB = cosineSimilarity(normalizehummingRTB, normalizeWindowRTB)
        windowSimilarityFTB = cosineSimilarity(normalizehummingFTB, normalizeWindowFTB)
        
        windowSim = windowSimilarityATB * 0.3 + windowSimilarityRTB * 0.2 + windowSimilarityFTB * 0.5
        windowSimilarity.append(windowSim)
    
    avgWindowSimilarity = np.mean(windowSimilarity)
    
    similarity = []
    print(f"Mengolah file dataset...  ")

    print(f"Dataset Paths: {datasetPath}")
    
    # Use provided uploadFolder or default to relative path
    if uploadFolder is None:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to ClassiQue directory and then to uploads
        uploadFolder = os.path.join(script_dir, '..', 'uploads')
        uploadFolder = os.path.abspath(uploadFolder)
    
    print(f"Upload folder: {uploadFolder}")
    
    for path in datasetPath:
        fullPath = os.path.join(uploadFolder, path)
        songNotes = readMIDI(fullPath)
        if songNotes.size == 0:
            continue
        
        songNotes = normalizeTempoPitch(songNotes)  
        
        songATB = extractATB(songNotes) 
        normalizeATB = normalizeHistogram(songATB)

        songRTB = extractRTB(songNotes)
        normalizeRTB = normalizeHistogram(songRTB)
        
        songFTB = extractFTB(songNotes)
        normalizeFTB = normalizeHistogram(songFTB)
        
        # Cosine Similarity untuk setiap fitur
        checkSimilarityATB = cosineSimilarity(normalizehummingATB, normalizeATB)
        checkSimilarityRTB = cosineSimilarity(normalizehummingRTB, normalizeRTB)
        checkSimilarityFTB = cosineSimilarity(normalizehummingFTB, normalizeFTB)
        
        totalSim = (checkSimilarityATB * 0.3 + checkSimilarityRTB * 0.2 + checkSimilarityFTB * 0.5) * 0.7 + avgWindowSimilarity * 0.3
        similarity.append((path, totalSim))
    
    similarity.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    print("Menampilkan hasil perbandingan...")
    
    # lanjutkan kode disini
    mapperData = loadMapper(mapper)
    if mapperData is None:
        return []

    # Proses untuk mendapatkan metadata dari mapper dan hasil akhir
    for songPath, simScore in similarity:
        # Mencari informasi lagu dari mapper berdasarkan nama file lagu
        songInfo = next((item for item in mapperData if isinstance(item, dict) and item.get('audio') == songPath), None)
        
        if songInfo:
            results.append({
            'Audio': songInfo['audio'],
            'Composer': songInfo.get('composer', 'Unknown'),
            'Similarity': f"{round(simScore * 100, 2)}%",  # Menampilkan hasil dalam persen
            'Album': songInfo.get('album', 'No image available')  # Menambahkan informasi album
            })
    
    # Menampilkan hasil akhir
    return results