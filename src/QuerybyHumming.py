import mido
import numpy as np
import json
import os

# Note : 03.26 WIB 8/12/2024 - lukas 
# jadi file dir nya masih harus disesuiakan dengan file yang ada di folder test
# perhitungan similarity nya 30% ATB, 20% RTB, 50% FTB, . Kenapa ? karena pembobotannya emang seperti itu (katanya) agar berharap dapat hasil akurat src chatgpt
# windowingnya 30, sliding step 6 / kenapa ? karena katanya musik klasik banyak yang menggunakan window size 30 dan sliding step 6 / src chatGPT
# kalo misalkan testing dengan copy audio dari folder test/music, nilainya tidak pas 100% karena baca di docs berikut : 
# link = https://docs.google.com/document/d/1Smi26AgL5O8hOdWg7o2P1gRFNTjSPAiUADXHchIVb3s/edit?usp=sharing
# Oh ya kalo ada tulisannya tiap fungsi itu bekas debugging
# jujur aku juga bingung. tapi aku coba baca dari sumber yang ada di chatGPT
# kalo mau testing ---------------------  hummingMIDIpath = '<input here>'  ---------------------
# belum error handling, jadi kalo error ya error aja, dan threshold tidak ada. jadi apabila lagu yang sebenarnya tidak ada di dataset, maka hasil yang dikeluarkan adalah lagu yang paling mirip dengan lagu yang diinputkan


# Bagian Pemrosesan Audio 
def readMIDI(filename):
    thisMidi = mido.MidiFile(filename)
    melodyNotes = []
    for track in thisMidi.tracks:
        for message in track:
            if message.type == 'note_on':
                melodyNotes.append(message.note)
    return melodyNotes  

# Fungsi Windowing
def windowing(melodyNotes, windowSize=30, slidingStep=6):
    windows = []
    for i in range(0, len(melodyNotes) - windowSize + 1, slidingStep):
        window = melodyNotes[i:i + windowSize]
        windows.append(window)
    return windows

# Normalisasi Tempo dan Pitch
def normalizeTempoPitch(notes):
    pitchMean = np.mean(notes)
    pitchStd = np.std(notes)
    normalized_notes = (notes - pitchMean) / pitchStd  # Normalisasi pitch
    return normalized_notes  # Menghindari konversi menjadi integer

# Ekstraksi Fitur
def extractATB(melodyNotes):
    hist = np.zeros(128)  # Histogram untuk 128 nada MIDI
    for note in melodyNotes:
        hist[int(note)] += 1
    return hist

def extractRTB(melodyNotes):
    hist = np.zeros(255)  # Histogram untuk interval nada dari -127 hingga +127
    for i in range(1, len(melodyNotes)):
        diff = int(melodyNotes[i] - melodyNotes[i - 1])
        if -127 <= diff <= 127:
            hist[diff + 127] += 1
    return hist 

def extractFTB(melodyNotes):
    hist = np.zeros(255)  # Histogram untuk perbedaan dengan nada pertama
    firstNote = melodyNotes[0]
    for note in melodyNotes:
        diff = int(note - firstNote)
        hist[diff + 127] += 1
    return hist

def loadMapper(mapper):
    print(f"Mencoba membuka file: {mapper}")
    if os.path.exists(mapper):
        with open(mapper, 'r') as f:
            return json.load(f)
    else:
        print(f"File {mapper} tidak ditemukan.")
        return None

# Normalisasi Histogram
def normalizeHistogram(hist):
    total = np.sum(hist)
    normHist = np.zeros_like(hist)
    if total < 1e-6:  # Jika total terlalu kecil, hindari pembagian
        return normHist  # Kembalikan histogram kosong atau tanpa perubahan
    normHist = hist / total  # Normalisasi histogram
    return normHist

# Cosine Similarity
def cosineSimilarity(vec1, vec2):
    dotProduct = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:  # Cek jika ada vektor dengan panjang 0
        return 0
    similarity = dotProduct / (norm1 * norm2)
    return min(max(similarity, -1), 1)

# Main Program
def querybyHumming(hummingMIDI, datasetPath, mapper):
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
    for path, sim in similarity: 
        songInfo = next((item for item in mapper if item['audio'] == path), None)
        if songInfo: 
            results.append((songInfo['audio'], songInfo['album'], sim))
    
    return results
