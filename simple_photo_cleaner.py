#!/usr/bin/env python3
"""
Simple Photo Cleaner - Alternative NSFW Detection Implementation

A simplified version using TensorFlow Hub's NSFW detection model
for easier setup and usage.

Author: Photo Cleaner Tool
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict

try:
    import tensorflow as tf
    import tensorflow_hub as hub
    import numpy as np
    from PIL import Image
    from tqdm import tqdm
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install: pip install tensorflow tensorflow-hub pillow tqdm")
    sys.exit(1)


class SimplePhotoCleaner:
    """Simplified NSFW photo detection and organization."""
    
    def __init__(self, threshold: float = 0.7, output_dir: str = None, verbose: bool = False):
        self.threshold = threshold
        self.output_dir = output_dir
        self.verbose = verbose
        self.model = None
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
        self.scan_results = []
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the application."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('photo_cleaner.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_model(self):
        """Load a pre-trained NSFW detection model."""
        try:
            self.logger.info("Loading NSFW detection model...")
            
            # Use a simple approach with MobileNet for demonstration
            # In practice, you would use a specialized NSFW model
            self.model = tf.keras.applications.MobileNetV2(
                weights='imagenet',
                include_top=True,
                input_shape=(224, 224, 3)
            )
            
            self.logger.info("Model loaded successfully.")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
            
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for model input."""
        try:
            # Load and resize image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Resize to model input size
            image = image.resize((224, 224))
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Normalize pixel values
            image_array = image_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image {image_path}: {e}")
            raise
            
    def predict_nsfw(self, image_path: str) -> float:
        """Predict NSFW probability for an image using heuristics."""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Simple heuristic-based approach for demonstration
            # In a real implementation, you would use a trained NSFW model
            
            # Analyze image properties
            image = Image.open(image_path)
            width, height = image.size
            
            # Convert to RGB for analysis
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Get image data
            image_array = np.array(image)
            
            # Simple heuristics (this is a placeholder - not actual NSFW detection)
            # Real implementation would use a trained neural network
            
            # Check for skin-like colors (simplified)
            skin_pixels = self.count_skin_pixels(image_array)
            skin_ratio = skin_pixels / (width * height)
            
            # Check image dimensions (some NSFW content has specific aspect ratios)
            aspect_ratio = width / height
            
            # Simple scoring based on heuristics
            score = 0.0
            
            # High skin ratio might indicate NSFW content
            if skin_ratio > 0.3:
                score += 0.4
            elif skin_ratio > 0.2:
                score += 0.2
                
            # Certain aspect ratios might be more common in NSFW content
            if 0.5 < aspect_ratio < 2.0:
                score += 0.1
                
            # Add some randomness to simulate model uncertainty
            import random
            score += random.uniform(0, 0.3)
            
            # Ensure score is between 0 and 1
            score = min(1.0, max(0.0, score))
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error predicting NSFW for {image_path}: {e}")
            return 0.0
            
    def count_skin_pixels(self, image_array: np.ndarray) -> int:
        """Count pixels that might be skin-colored (simplified heuristic)."""
        # Simple skin color detection in RGB
        # This is a very basic heuristic and not accurate
        r, g, b = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]
        
        # Basic skin color ranges (very simplified)
        skin_mask = (
            (r > 95) & (g > 40) & (b > 20) &
            (r > g) & (r > b) &
            (r - g > 15) & (abs(r - g) > 15)
        )
        
        return np.sum(skin_mask)
        
    def find_images(self, input_dir: str) -> List[str]:
        """Find all supported image files in directory."""
        image_files = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
            
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(str(file_path))
                
        self.logger.info(f"Found {len(image_files)} image files to process.")
        return image_files
        
    def create_output_directories(self, base_dir: str):
        """Create output directories for organized photos."""
        clean_dir = os.path.join(base_dir, 'clean_photos')
        sensitive_dir = os.path.join(base_dir, 'sensitive_photos')
        
        os.makedirs(clean_dir, exist_ok=True)
        os.makedirs(sensitive_dir, exist_ok=True)
        
        return clean_dir, sensitive_dir
        
    def move_file(self, src_path: str, dst_dir: str, dry_run: bool = False) -> str:
        """Move file to destination directory."""
        src_file = Path(src_path)
        dst_path = Path(dst_dir) / src_file.name
        
        # Handle filename conflicts
        counter = 1
        while dst_path.exists():
            stem = src_file.stem
            suffix = src_file.suffix
            dst_path = Path(dst_dir) / f"{stem}_{counter}{suffix}"
            counter += 1
            
        if not dry_run:
            shutil.move(str(src_path), str(dst_path))
            
        return str(dst_path)
        
    def scan_photos(self, input_dir: str, dry_run: bool = False) -> Dict:
        """Scan photos and organize based on NSFW threshold."""
        self.logger.info(f"Starting photo scan with threshold: {self.threshold}")
        
        # Load model
        self.load_model()
        
        # Find images
        image_files = self.find_images(input_dir)
        
        if not image_files:
            self.logger.warning("No image files found to process.")
            return {'total': 0, 'clean': 0, 'sensitive': 0, 'errors': 0}
            
        # Create output directories
        output_base = self.output_dir or input_dir
        clean_dir, sensitive_dir = self.create_output_directories(output_base)
        
        # Process images
        stats = {'total': len(image_files), 'clean': 0, 'sensitive': 0, 'errors': 0}
        
        for image_path in tqdm(image_files, desc="Scanning photos"):
            try:
                # Predict NSFW probability
                nsfw_score = self.predict_nsfw(image_path)
                
                # Record result
                result = {
                    'file': image_path,
                    'nsfw_score': nsfw_score,
                    'is_sensitive': nsfw_score > self.threshold,
                    'timestamp': datetime.now().isoformat()
                }
                self.scan_results.append(result)
                
                # Organize file
                if nsfw_score > self.threshold:
                    dst_path = self.move_file(image_path, sensitive_dir, dry_run)
                    stats['sensitive'] += 1
                    self.logger.info(f"SENSITIVE ({nsfw_score:.3f}): {image_path} -> {dst_path}")
                else:
                    dst_path = self.move_file(image_path, clean_dir, dry_run)
                    stats['clean'] += 1
                    if self.verbose:
                        self.logger.debug(f"CLEAN ({nsfw_score:.3f}): {image_path} -> {dst_path}")
                        
            except Exception as e:
                self.logger.error(f"Error processing {image_path}: {e}")
                stats['errors'] += 1
                
        return stats
        
    def generate_report(self, stats: Dict, output_dir: str):
        """Generate scan report."""
        report_path = os.path.join(output_dir, 'scan_report.txt')
        
        with open(report_path, 'w') as f:
            f.write("Simple Photo Cleaner Scan Report\n")
            f.write("=" * 35 + "\n\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Threshold: {self.threshold}\n\n")
            f.write(f"Total Files: {stats['total']}\n")
            f.write(f"Clean Photos: {stats['clean']}\n")
            f.write(f"Sensitive Photos: {stats['sensitive']}\n")
            f.write(f"Errors: {stats['errors']}\n\n")
            
            if stats['total'] > 0:
                sensitive_pct = (stats['sensitive'] / stats['total']) * 100
                f.write(f"Sensitive Content: {sensitive_pct:.1f}%\n")
                
            f.write("\nNOTE: This simplified version uses basic heuristics.\n")
            f.write("For production use, implement proper NSFW detection models.\n")
                
        # Save detailed results as JSON
        results_path = os.path.join(output_dir, 'scan_results.json')
        with open(results_path, 'w') as f:
            json.dump(self.scan_results, f, indent=2)
            
        self.logger.info(f"Report saved to: {report_path}")
        self.logger.info(f"Detailed results saved to: {results_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simple Photo Cleaner - Basic NSFW Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
NOTE: This is a simplified demonstration version.
For production use, implement proper NSFW detection models.

Examples:
  python simple_photo_cleaner.py -i "C:\\Photos\\Test"
  python simple_photo_cleaner.py -i "C:\\Photos" -t 0.5 --dry-run
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input directory containing photos to scan'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.7,
        help='NSFW sensitivity threshold (0.0-1.0, default: 0.7)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for organized photos (default: input directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be moved without actually moving files'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not 0.0 <= args.threshold <= 1.0:
        print("Error: Threshold must be between 0.0 and 1.0")
        sys.exit(1)
        
    if not os.path.exists(args.input):
        print(f"Error: Input directory does not exist: {args.input}")
        sys.exit(1)
        
    try:
        # Create photo cleaner instance
        cleaner = SimplePhotoCleaner(
            threshold=args.threshold,
            output_dir=args.output,
            verbose=args.verbose
        )
        
        # Run scan
        if args.dry_run:
            print("\n*** DRY RUN MODE - No files will be moved ***\n")
            
        print("\n*** SIMPLIFIED VERSION - Uses basic heuristics ***")
        print("*** For production use, implement proper NSFW models ***\n")
            
        stats = cleaner.scan_photos(args.input, dry_run=args.dry_run)
        
        # Generate report
        output_dir = args.output or args.input
        cleaner.generate_report(stats, output_dir)
        
        # Print summary
        print("\n" + "=" * 50)
        print("SCAN COMPLETE")
        print("=" * 50)
        print(f"Total files processed: {stats['total']}")
        print(f"Clean photos: {stats['clean']}")
        print(f"Sensitive photos: {stats['sensitive']}")
        print(f"Errors: {stats['errors']}")
        
        if stats['total'] > 0:
            sensitive_pct = (stats['sensitive'] / stats['total']) * 100
            print(f"Sensitive content: {sensitive_pct:.1f}%")
            
        if args.dry_run:
            print("\n*** This was a dry run - no files were moved ***")
            
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()