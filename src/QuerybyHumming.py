import mido
import numpy as np
import json
import os
import time

# Bagian Pemrosesan Audio 
def readMIDI(filename):
    """Membaca file MIDI dan mengekstrak catatan melodi."""
    thisMidi = mido.MidiFile(filename)
    melodyNotes = []
    for track in thisMidi.tracks:
        for message in track:
            if message.type == 'note_on':
                melodyNotes.append(message.note)
    return melodyNotes  

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
    pitchMean = np.mean(notes)
    pitchStd = np.std(notes)
    normalized_notes = (notes - pitchMean) / pitchStd  # Normalisasi pitch
    return normalized_notes

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

def loadMapper(mapper):
    """Memuat metadata mapper dari file JSON."""
    print(f"Mencoba membuka file: {mapper}")
    if os.path.exists(mapper):
        with open(mapper, 'r') as f:
            return json.load(f)
    else:
        print(f"File {mapper} tidak ditemukan.")
        return None

# Normalisasi Histogram
def normalizeHistogram(hist):
    """Normalisasi histogram."""
    total = np.sum(hist)
    normHist = np.zeros_like(hist)
    if total < 1e-6:  # Jika total terlalu kecil, hindari pembagian
        return normHist  # Kembalikan histogram kosong atau tanpa perubahan
    normHist = hist / total  # Normalisasi histogram
    return normHist

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
def querybyHumming(hummingMIDI, datasetPath, mapper):
    """Melakukan pencocokan berdasarkan humming MIDI."""
    print("Membaca file humming MIDI...")
    hummingNotes = readMIDI(hummingMIDI)
    print("Pembacaan file humming selesai.")
    
    # Normalisasi tempo dan pitch pada humming
    print("Normalisasi tempo dan pitch...")
    hummingNotes = normalizeTempoPitch(np.array(hummingNotes))  
    
    # Ekstraksi fitur global (ATB, RTB, FTB)
    print("Ekstraksi ATB...")
    hummingATB = extractATB(hummingNotes)
    normalizehummingATB = normalizeHistogram(hummingATB)
    
    print("Ekstraksi RTB...")
    hummingRTB = extractRTB(hummingNotes)
    normalizehummingRTB = normalizeHistogram(hummingRTB)
    
    print("Ekstraksi FTB...")
    hummingFTB = extractFTB(hummingNotes)
    normalizehummingFTB = normalizeHistogram(hummingFTB)   
    
    # Windowing
    windowedHumming = windowing(hummingNotes, windowSize=30, slidingStep=6)
    
    # Similarity untuk setiap window
    windowSimilarity = []
    for window in windowedHumming:
        # Normalisasi tempo dan pitch untuk setiap window
        windowNotes = normalizeTempoPitch(np.array(window))
        
        # Ekstraksi fitur untuk window
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
        
        # Normalisasi total similarity untuk window
        windowSim = windowSimilarityATB * 0.3 + windowSimilarityRTB * 0.2 + windowSimilarityFTB * 0.5
        windowSimilarity.append(windowSim)
    
    # Rata-rata similarity untuk seluruh window
    avgWindowSimilarity = np.mean(windowSimilarity)
    
    similarity = []
    print(f"Mengolah file dataset...  ")
    for path in datasetPath:
        songNotes = readMIDI(path)
        
        # Normalisasi tempo dan pitch pada lagu dataset
        songNotes = normalizeTempoPitch(np.array(songNotes))  # Pastikan ini dalam format array
        
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
        
        # Gabungkan similarity dari fitur global dan window
        totalSim = (checkSimilarityATB * 0.3 + checkSimilarityRTB * 0.2 + checkSimilarityFTB * 0.5) * 0.7 + avgWindowSimilarity * 0.3
        similarity.append((path, totalSim))
    
    # Urutkan berdasarkan similarity
    similarity.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    print("Menampilkan hasil perbandingan...")

    # Menampilkan hasil dengan nama audio, composer, dan similarity
    for path, sim in similarity:
        songInfo = next((item for item in mapper if item['audio'] == path), None)
        if songInfo: 
            results.append({
                'Audio': songInfo['audio'],
                'Composer': songInfo['composer'],
                'Similarity': round(sim, 2)
            })

    # Menampilkan hasil seperti format image_process.py
    for result in results:
        print(f"Audio: {result['Audio']}, Composer: {result['Composer']}, Similarity: {result['Similarity']}")

    return results

def loadMetadata(metadata_path):
    """Memuat metadata dari mapper.json"""
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    with open(metadata_path, 'r') as file:
        return json.load(file)

def main(query_folder, database_folder):
    start_time = time.time()
    
    # Load metadata
    metadata_path = os.path.join(database_folder, 'mapper.json')
    mapper = loadMetadata(metadata_path)
    
    # Temukan file MIDI query
    query_files = [f for f in os.listdir(query_folder) if f.endswith('.mid')]
    
    # Pastikan hanya ada satu file MIDI
    if not query_files:
        raise FileNotFoundError("Tidak ada file MIDI ditemukan di folder query")
    
    hummingMIDI = os.path.join(query_folder, query_files[0])
    query_audio_name = query_files[0]  # Nama audio query
    
    # Get all dataset MIDI paths
    datasetPaths = [os.path.join(database_folder, f) for f in os.listdir(database_folder) if f.endswith('.mid') and f != query_audio_name]
    
    # Query by humming
    print(f"Query Audio: {query_audio_name}")
    print("Menjalankan pencocokan berdasarkan humming...")
    
    # Normalisasi tempo dan pitch pada humming
    hummingNotes = readMIDI(hummingMIDI)
    hummingNotes = normalizeTempoPitch(np.array(hummingNotes))  
    
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
        # Normalisasi tempo dan pitch untuk setiap window
        windowNotes = normalizeTempoPitch(np.array(window))
        
        # Ekstraksi fitur untuk window
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
        
        # Normalisasi total similarity untuk window
        windowSim = windowSimilarityATB * 0.3 + windowSimilarityRTB * 0.2 + windowSimilarityFTB * 0.5
        windowSimilarity.append(windowSim)
    
    # Rata-rata similarity untuk seluruh window
    avgWindowSimilarity = np.mean(windowSimilarity)
    
    similarities = []
    print("Memproses database audio...")
    for path in datasetPaths:
        songNotes = readMIDI(path)
        
        # Normalisasi tempo dan pitch pada lagu dataset
        songNotes = normalizeTempoPitch(np.array(songNotes))
        
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
        
        # Gabungkan similarity dari fitur global dan window
        totalSim = (checkSimilarityATB * 0.3 + checkSimilarityRTB * 0.2 + checkSimilarityFTB * 0.5) * 0.7 + avgWindowSimilarity * 0.3
        similarities.append((path, totalSim))
    
    # Urutkan berdasarkan similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    print("\nHasil Perbandingan:")

    for path, sim in similarities:
        filename = os.path.basename(path)
        songInfo = next((item for item in mapper if item['audio'] == filename), None)
        
        if songInfo: 
            results.append({
                'Audio': filename,
                'Composer': songInfo['composer'],
                'Similarity': round(sim, 2)
            })

    # Tampilkan hasil
    for result in results:
        print(f"Audio: {result['Audio']}, Composer: {result['Composer']}, Similarity: {result['Similarity']}")

    end_time = time.time()
    print(f"\nTotal runtime: {end_time - start_time:.2f} detik")
    
    return results

if __name__ == "__main__":
    query_folder = "./ClassiQue/query-file"  
    database_folder = "./ClassiQue/uploads"  
    main(query_folder, database_folder)