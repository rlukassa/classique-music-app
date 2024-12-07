from PIL import Image
import numpy as np

# IMAGE PREPROCESSING: GRAYSCALE, RESIZE, AND FLATTEN

def grayscale_and_resize(image_path, target_size):
    ### 1 BUAH IMAGE
    # Open image
    image = Image.open(image_path)

    # Convert image to array
    image_array = np.array(image)

    # Grayscale the array
    if len(image_array.shape) == 3: # Jika image memiliki 3 channel yaitu RGB (artinya image berwarna)
        grayscale_image = np.dot(image_array[...,:3], [0.2989, 0.5870, 0.1140]) # Dot product tiap pixel RGB dengan nilai grayscale
    else: # Jika image sudah grayscale 
        grayscale_image = image_array

    # Normalize to 0-255 and cast to uint8
    grayscale_image = np.clip(grayscale_image, 0, 255).astype(np.uint8)

    # Perhitungan skala untuk resize
    input_height, input_width = grayscale_image.shape
    output_width, output_height = target_size
    row_scale = input_height / output_height
    col_scale = input_width / output_width

    # Membuat array of indices untuk row dan col
    row_indices = (np.arange(output_height) * row_scale).astype(int)
    col_indices = (np.arange(output_width) * col_scale).astype(int)
    
    # Resize image
    resized_img = grayscale_image[row_indices][:, col_indices]
    
    return resized_img

def flatten_1d(image_array):
    ### 1 BUAH IMAGE
    # Inisialisasi array 1D
    flatten_image = []

    # Iterasi melalui tiap elemen array 2D
    for row in image_array:
        for pixel in row:
            flatten_image.append(pixel) # Append pixel terurut

    # Convert ke numpy array
    flatten_image = np.array(flatten_image)

    return flatten_image


# DATA PREPROCESSING: STANDARDIZATION

def standardize_data(images_data):
    ### BANYAK IMAGE / DATASET IMAGE
    means = [0] * images_data.shape[1] # Length = jumlah pixel per gambar

    for j in range(images_data.shape[1]): # Iterasi tiap pixel (kolom)
        sum = 0
        for i in range(images_data.shape[0]): # Iterasi tiap gambar (baris)
            sum += images_data[i, j]
        means[j] = sum / images_data.shape[0] # Rata-rata pixel ke-j (per kolom)
    
    # Mengurangi tiap pixel dengan mean pixel tersebut
    centered_data = np.copy(images_data)
    centered_data -= means

    return means, centered_data


# DATA PROCESSING & MATHEMATICAL OPERATION

def eigen(matrix):
    # Menerima matrix persegi
    

def pca(centerized_data):
    ### BANYAK IMAGE / DATASET IMAGE
    # Menghitung covariance matrix (C) dulu
    # C = (X^T * X) / n
        # X = centerized_data
    N = centerized_data.shape[0]
    covariance_matrix = np.dot(centerized_data.T, centerized_data) / N

    # Ambil row dan col dari covariance matrix
    row, col = covariance_matrix.shape

    # Dekomposisi SVD
    # C = U * Sigma * V^T
    U, Sigma, Vt = np.linalg.svd(covariance_matrix)

    # Ambil principal component / komponen utama sebanyak N
    # Principal component = U
    principal_component = U[:, :N]

    # Z = X' * U
    Z = np.dot(centerized_data, principal_component)

    return principal_component, Z