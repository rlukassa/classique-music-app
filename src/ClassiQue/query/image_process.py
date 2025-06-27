from PIL import Image
import numpy as np
import os
import json

def grayscale_and_resize(image_path, target_size):
    """Convert image to grayscale and resize to target_size using manual RGB manipulation."""
    try:
        # Open image and convert to RGB to ensure consistency
        image = Image.open(image_path)
        
        # Convert to RGB if it's not already (handles RGBA, LA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert image to numpy array
        image_array = np.array(image)

        # Ensure we have a valid RGB image after conversion
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # Apply RGB to grayscale conversion formula
            grayscale_image = np.dot(image_array, [0.2989, 0.5870, 0.1140])
        elif len(image_array.shape) == 3 and image_array.shape[2] == 4:
            # RGBA image, use only RGB channels
            grayscale_image = np.dot(image_array[...,:3], [0.2989, 0.5870, 0.1140])
        elif len(image_array.shape) == 3 and image_array.shape[2] == 1:
            # Single channel image in 3D array
            grayscale_image = image_array.squeeze()
        elif len(image_array.shape) == 2:
            # Already grayscale (2D array)
            grayscale_image = image_array
        else:
            # Fallback: convert using PIL's built-in grayscale conversion
            grayscale_pil = image.convert('L')
            grayscale_image = np.array(grayscale_pil)

        # Normalize to 0-255 and convert to uint8
        grayscale_image = np.clip(grayscale_image, 0, 255).astype(np.uint8)
        
    except Exception as e:
        print(f"Error in grayscale conversion for {image_path}: {e}")
        # Fallback: use PIL's built-in conversion
        try:
            image = Image.open(image_path)
            grayscale_pil = image.convert('L')
            grayscale_image = np.array(grayscale_pil)
        except Exception as fallback_error:
            print(f"Fallback conversion also failed for {image_path}: {fallback_error}")
            raise fallback_error

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
    
    # Pastikan folder_path adalah string
    if not isinstance(folder_path, (str, bytes, os.PathLike)):
        raise TypeError(f"Expected folder_path to be string, bytes, or os.PathLike, got {type(folder_path)}")

    for filename in os.listdir(folder_path):
        # Skip hidden files and macOS system files
        if filename.startswith('.') or filename.startswith('._'):
            continue
            
        filepath = os.path.join(folder_path, filename)
        _, ext = os.path.splitext(filename)  # Get file extension
        
        if os.path.isfile(filepath) and ext.lower() in valid_extensions:  # Check if file is valid image
            try:
                # Check if file is readable as image
                with Image.open(filepath) as test_img:
                    test_img.verify()  # Verify image integrity
                
                # Reopen image for processing (verify() can corrupt the image object)
                test_img = Image.open(filepath)
                test_img.load()  # Ensure image is fully loaded
                
                # Process the image
                image_array = grayscale_and_resize(filepath, target_size)
                flattened_image = flatten_1d(image_array)
                images.append(flattened_image)
                filenames.append(filename)
                print(f"Successfully processed {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                print(f"Skipping {filename} due to processing error")
                continue
    
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
    U, _, _ = np.linalg.svd(covariance_matrix)
    principal_components = U
    projections = np.dot(centerized_data, principal_components)
    return principal_components, projections

def calculate_similarity(projection1, projection2):
    """Calculate similarity as the cosine similarity between two vectors."""
    dot_product = np.dot(projection1, projection2)
    norm1 = np.linalg.norm(projection1)
    norm2 = np.linalg.norm(projection2)
    return dot_product / (norm1 * norm2)

def find_top_similar_images(input_image_projection, database_projections, filenames):
    """Find the top N most similar images in the database to the input image with a similarity threshold."""
    similarities = [calculate_similarity(input_image_projection, db_proj) for db_proj in database_projections]
    sorted_indices = np.argsort(similarities)[::-1]  # Sort in descending order
    
    # Filter berdasarkan threshold
    filtered_indices = [i for i in sorted_indices if similarities[i]]
    
    # Ambil top_n dari hasil yang lolos threshold
    top_indices = filtered_indices[:]
    return [(filenames[i], similarities[i]) for i in top_indices]

def loadMapper(mapper, search_path):  # Remove default path to force explicit path passing 
    if isinstance(mapper, list):
        mapper = mapper[0]
    mapper_path = os.path.join(search_path, mapper)
    if os.path.exists(mapper_path):
        with open(mapper_path, "r") as f:
            return json.load(f)
    else:
        print(f"File {mapper} not found in {search_path}")
        return None


def main(input_image_path, database_folder, mapper, target_size=(75, 75)):
    """Membandingkan gambar input dengan gambar di database dan menemukan yang paling mirip."""
    mapper = loadMapper(mapper, database_folder)  # Pass the correct search path
    if mapper is None: 
        return []
    print("Memuat gambar dari folder database...")

    # Memuat dan memproses gambar dari database
    database_images, filenames = load_images_from_folder(database_folder, target_size)
    means, centered_database_images = standardize_data(database_images)

    # Melakukan PCA pada gambar database
    principal_components, database_projections = pca(centered_database_images)

    # Memproses gambar input
    input_image = grayscale_and_resize(input_image_path, target_size)
    input_image_flattened = flatten_1d(input_image)
    input_image_centered = input_image_flattened - means

    # Proyeksi gambar input ke komponen utama
    input_image_projection = np.dot(input_image_centered, principal_components)
    
    # Mencari gambar paling mirip dengan threshold 0.8
    top_similar_images = find_top_similar_images(input_image_projection, database_projections, filenames)
    
    top_similar_images.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    
    for filename, similarity in top_similar_images:
        fileInfo = next((item for item in mapper if item["album"] == filename), None)
        
        if fileInfo : 
            results.append({
            'Audio' : fileInfo['audio'],
            'Composer' : fileInfo.get('composer', 'Unknown'),
            'Similarity' : f"{round(similarity * 100, 2)}%",
            'Album' : fileInfo['album'],
            })
    
    return results if results else []
