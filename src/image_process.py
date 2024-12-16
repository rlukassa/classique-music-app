from PIL import Image
import numpy as np
import os
import json
import time  # Tambahkan modul time untuk tracking runtime

def grayscale_and_resize(image_path, target_size):
    """Convert image to grayscale and resize to target_size using manual RGB manipulation."""
    # Open image
    image = Image.open(image_path)

    # Convert image to numpy array
    image_array = np.array(image)

    # Convert to grayscale manually if image has RGB channels
    if len(image_array.shape) == 3:  # Image has RGB channels
        grayscale_image = np.dot(image_array[...,:3], [0.2989, 0.5870, 0.1140])  # Apply grayscale formula
    else:  # Image is already grayscale
        grayscale_image = image_array

    # Normalize to 0-255 and convert to uint8
    grayscale_image = np.clip(grayscale_image, 0, 255).astype(np.uint8)

    # Resize the grayscale image
    input_height, input_width = grayscale_image.shape
    output_width, output_height = target_size
    row_scale = input_height / output_height
    col_scale = input_width / output_width

    # Create indices for resizing
    row_indices = (np.arange(output_height) * row_scale).astype(int)
    col_indices = (np.arange(output_width) * col_scale).astype(int)

    resized_image = grayscale_image[row_indices][:, col_indices]

    return resized_image

def flatten_1d(image_array):
    """Flatten a 2D image array into a 1D array."""
    return image_array.flatten()

def load_images_from_folder(folder_path, target_size):
    """Load all images from a folder, preprocess them, and return as a matrix."""
    images = []
    filenames = []
    valid_extensions = {".jpeg", ".jpg", ".png"}  # Valid image formats
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        _, ext = os.path.splitext(filename)  # Get file extension
        
        if os.path.isfile(filepath) and ext.lower() in valid_extensions and filename != "mapper.json":  # Exclude mapper.json
            try:
                image_array = grayscale_and_resize(filepath, target_size)
                flattened_image = flatten_1d(image_array)
                images.append(flattened_image)
                filenames.append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return np.array(images), filenames

def standardize_data(images_data):
    """Standardize dataset by centering each pixel around its mean."""
    means = np.mean(images_data, axis=0)
    centered_data = images_data - means
    return means, centered_data

def pca(centerized_data):
    """Perform PCA on the dataset and return principal components and projections."""
    N = centerized_data.shape[0]
    covariance_matrix = np.dot(centerized_data.T, centerized_data) / N
    U, Sigma, Vt = np.linalg.svd(covariance_matrix)
    principal_components = U
    projections = np.dot(centerized_data, principal_components)
    return principal_components, projections

def calculate_similarity(projection1, projection2):
    """Calculate similarity as the cosine similarity between two vectors."""
    # Pastikan vektor tidak semuanya nol
    if np.all(projection1 == 0) or np.all(projection2 == 0):
        return 0.0
    
    dot_product = np.dot(projection1, projection2)
    norm1 = np.linalg.norm(projection1)
    norm2 = np.linalg.norm(projection2)
    
    # Hindari pembagian oleh nol
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Pastikan hasil dalam rentang [-1, 1], kemudian normalisasi ke [0, 1]
    cosine_similarity = dot_product / (norm1 * norm2)
    
    # Normalisasi ke rentang [0, 1]
    return (cosine_similarity + 1) / 2

def load_metadata(metadata_path):
    """Load metadata from mapper.json and organize it by image filename."""
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    with open(metadata_path, 'r') as file:
        raw_metadata = json.load(file)
    
    metadata = {}
    for entry in raw_metadata:
        # Gunakan nama file gambar sebagai kunci
        album_image = entry.get("album", "")
        if album_image:
            metadata[album_image] = {
                "Nama": album_image,
                "Composer": entry.get("composer", "Unknown"),
                "Album": "Unknown"  # Karena tidak ada informasi album spesifik
            }
    return metadata

def find_all_similar_images(input_image_projection, database_projections, filenames, metadata):
    """Find all images in the database and return their similarity scores."""
    similarities = [calculate_similarity(input_image_projection, db_proj) for db_proj in database_projections]
    result = []

    for filename, similarity in zip(filenames, similarities):
        # Gunakan nama file sebagai kunci untuk metadata
        meta = metadata.get(filename, {
            "Nama": filename,
            "Composer": "Unknown", 
            "Album": "Unknown"
        })
        
        result.append({
            "Nama": meta["Nama"],
            "Composer": meta["Composer"],
            "Album": meta["Album"],
            "Similarity": round(similarity, 2)
        })

    # Sort results by similarity in descending order
    result.sort(key=lambda x: x['Similarity'], reverse=True)

    return result

def get_query_image(query_folder):
    """Retrieve the first valid image file from the query folder."""
    valid_extensions = {".jpeg", ".jpg", ".png"}
    for filename in os.listdir(query_folder):
        filepath = os.path.join(query_folder, filename)
        _, ext = os.path.splitext(filename)
        if os.path.isfile(filepath) and ext.lower() in valid_extensions:
            return filepath
    raise FileNotFoundError(f"No valid image files found in folder: {query_folder}")

def main(query_folder, database_folder, target_size=(70, 70)):
    """Compare an input image with a database of images and return similarity results."""
    # Mulai hitung waktu
    start_time = time.time()

    print("Loading metadata...")
    metadata_path = os.path.join(database_folder, "mapper.json")
    metadata = load_metadata(metadata_path)

    print("Loading images from database folder...")
    # Load and preprocess the database images
    database_images, filenames = load_images_from_folder(database_folder, target_size)
    means, centered_database_images = standardize_data(database_images)

    # Perform PCA on the database images
    principal_components, database_projections = pca(centered_database_images)

    # Get the query image
    query_image_path = get_query_image(query_folder)
    print(f"Query image path: {query_image_path}")

    # Preprocess the query image
    input_image = grayscale_and_resize(query_image_path, target_size)
    input_image_flattened = flatten_1d(input_image)
    input_image_centered = input_image_flattened - means

    # Project the query image onto the principal components
    input_image_projection = np.dot(input_image_centered, principal_components)

    # Find all similar images
    all_similar_images = find_all_similar_images(input_image_projection, database_projections, filenames, metadata)

    # Print results
    print("Similar Images:")
    for img in all_similar_images:
        print(f"Image: {img['Nama']}, Composer: {img['Composer']}, Similarity: {img['Similarity']}")

    # Hitung dan cetak runtime
    end_time = time.time()
    runtime = end_time - start_time
    print(f"\nTotal Runtime: {runtime:.4f} detik")

# Run the main function
if __name__ == "__main__":
    query_folder = "./ClassiQue/query-file"  # Path to the folder containing the query image
    database_folder = "./ClassiQue/uploads"  # Path to the folder containing database images
    main(query_folder, database_folder)