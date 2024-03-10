# Texture Generation Tool

## Overview

The Texture Generation Tool is an automated script for creating textures for 3D models and graphic applications. It places defects or special features on a base color map. After the defects have been placed, the tool generates a normal map for each created texture to create the illusion of depth and detail on an otherwise flat surface. This Tool can be implemented in a synthetic data render pipeline. 

## Functionality

The tool uses a combination of image processing functions and algorithms to realistically and controllably arrange the textures on a base color map and create normal maps:

### Smoothing by Gaussian Filtering

- **Function:** `smooth_gaussian`
- **Description:** Reduces image noise and smooths the image by applying a Gaussian blur to create a basis for reliable edge extraction.

### Sobel Operator for Edge Extraction

- **Function:** `sobel`
- **Description:** Extracts precise edge information from the smoothed image by applying the Sobel operator. This information is crucial for creating the normal map.

### Normal Map Calculation

- **Function:** `compute_normal_map`
- **Description:** Calculates the normal map from the extracted gradients. The normal map represents the variance of the surface used in rendering light and shadow on 3D surfaces.

### Inserting Textures

- **Functions:** `create_cylinder_mask`, `insert_texture`, `insert_random_textures`
- **Description:** Creates a cylindrical mask to control the placement of defects. Defects are then randomly inserted within the area defined by the mask. The number and position of defects are determined by a random logic. Each defect is labeled and written into a bounding box file that can be used for machine learning.

## Configuration and Parameters

Before the tool can be used, certain parameters must be adjusted:

### General Settings

- `background_image_path`: The path to the base image on which the textures are placed.
- `defect_folder_path`: The path to the folder containing the defects to be placed on the base image.
- `output_basecolor_image_dir`: The path to save the base color images with inserted defects.
- `x_position`, `y_position`: The X and Y coordinates on the base image to define the central point (midpoint) for the mask.
- `inner_radius`, `outer_radius`: Define the cylindrical area around the central point where the defects are placed.
- `number_of_images`: The number of textures to be generated.

### Normal Map Settings

- `input_dir`: The path to the folder with the generated textures (should be the same as `output_basecolor_image_dir`).
- `output_dir`: The path to the folder where the normal maps should be saved.
- `smoothness`: The smoothness strength applied before creating the normal map.
- `intensity`: The intensity of the normals in the normal map.

## Instructions for Use

1. Check and ensure that the required raw data and textures are in the appropriate folders (`texture/raw` and `texture/defects/ps`).
2. Adjust the parameters in the script according to your specific requirements.
3. Run the script. The tool will automatically place the textures on the base color map and create normal maps for each generated texture.
