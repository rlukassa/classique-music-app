from PIL import Image
import numpy as np
import os

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
    valid_extensions = {".jpeg", ".jpg", ".png", ".bmp", ".tiff", ".gif"}  # Valid image formats
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        _, ext = os.path.splitext(filename)  # Get file extension
        
        if os.path.isfile(filepath) and ext.lower() in valid_extensions:  # Check if file is valid image
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
    dot_product = np.dot(projection1, projection2)
    norm1 = np.linalg.norm(projection1)
    norm2 = np.linalg.norm(projection2)
    return dot_product / (norm1 * norm2)

def find_top_similar_images(input_image_projection, database_projections, filenames, top_n=3, threshold=0.8):
    """Find the top N most similar images in the database to the input image with a similarity threshold."""
    similarities = [calculate_similarity(input_image_projection, db_proj) for db_proj in database_projections]
    sorted_indices = np.argsort(similarities)[::-1]  # Sort in descending order
    
    # Filter berdasarkan threshold
    filtered_indices = [i for i in sorted_indices if similarities[i] >= threshold]
    
    # Ambil top_n dari hasil yang lolos threshold
    top_indices = filtered_indices[:top_n]
    return [(filenames[i], similarities[i]) for i in top_indices]


def main(input_image_path, database_folder, target_size=(75, 75)): # Reduce the scale for faster runtime --> Reducing this will reduce the accuracy too
    """Compare an input image with a database of images and find the top similar ones."""
    print("Loading images from database folder...")

    # Load and preprocess the database images
    database_images, filenames = load_images_from_folder(database_folder, target_size)
    means, centered_database_images = standardize_data(database_images)

    # Perform PCA on the database images
    principal_components, database_projections = pca(centered_database_images)

    # Preprocess the input image
    input_image = grayscale_and_resize(input_image_path, target_size)
    input_image_flattened = flatten_1d(input_image)
    input_image_centered = input_image_flattened - means

    # Project the input image onto the principal components
    input_image_projection = np.dot(input_image_centered, principal_components)
    
    # Find the top 3 most similar images with a threshold of 0.8
    top_similar_images = find_top_similar_images(input_image_projection, database_projections, filenames, top_n=3, threshold=0.8)


    print("3 gambar paling mirip:")
    for idx, (image_name, similarity_score) in enumerate(top_similar_images, start=1):
        print(f"{idx}. {image_name} dengan tinggkat kesamaan: {similarity_score:.2f}")

    # Check for images with similarity above 80%
    high_similarity_images = [img for img in top_similar_images if img[1] >= 0.8]

    if high_similarity_images:
        print("\nGambar yang mirip (similarity percentage >= 0.8):")
        for image_name, similarity_score in high_similarity_images:
            print(f"- {image_name} with similarity score: {similarity_score:.2f}")
    else:
        print("\nTidak ada gambar yang dianggap mirip")

# Run the main function
if __name__ == "__main__":
    input_image_path = "./test/photo_raw/balakir.jpg"  # Path to the input image
    database_folder = "./test/photo_raw"  # Path to the folder containing database images
    main(input_image_path, database_folder)
