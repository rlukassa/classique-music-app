from QuerybyHumming import querybyHumming
from QuerybyHumming import loadMapper
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test')))
from datasetPath import datasetPath

if __name__ == "__main__":
    hummingMidiPath = '../test/islameitest.mid' # INPUT HERE, sesuaikan dengan path file midi yang ingin diuji
    Mapper = loadMapper('../test/mapper.json')  

    results = querybyHumming(hummingMidiPath, datasetPath, Mapper)

    if results:
        bestMatch = max(results, key=lambda x: x[2])
        print(f"Audio: {bestMatch[0]}")
        print(f"Album: {bestMatch[1]}")
        print(f"Similarity: {bestMatch[2]}")
