# Photo Cleaner - NSFW Content Detection Tool

A Python application that automatically scans photos for NSFW (Not Safe For Work) content and organizes them into appropriate folders based on sensitivity thresholds.

## Features

- **Automated NSFW Detection**: Uses OpenNSFW2 model for accurate content classification
- **Configurable Sensitivity**: Set custom thresholds for content filtering (default: 70%)
- **Automatic Organization**: Moves sensitive content to a dedicated folder
- **Batch Processing**: Scan entire directories of photos
- **Safe Operation**: Creates backups and logs all operations
- **Multiple Formats**: Supports JPG, PNG, GIF, BMP, and TIFF image formats
- **User-Friendly GUI**: Modern graphical interface for easy operation

## Requirements

- Python 3.7+
- TensorFlow 2.x
- OpenCV
- NumPy
- Pillow (PIL)
- CustomTkinter (for GUI)

## Installation

1. Clone or download repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. The script will automatically download the OpenNSFW2 model on first run

## Usage

### Graphical User Interface (GUI)

The easiest way to use Photo Cleaner is through its graphical interface:

1. On Windows, double-click `run_gui.bat`
2. On other platforms, run: `python photo_cleaner_gui.py`

The GUI provides intuitive controls for:
- Selecting input and output directories
- Adjusting sensitivity threshold with a slider
- Choosing between simple and advanced detection modes
- Enabling dry run mode for previewing results
- Viewing real-time logs and progress
- Accessing reports and organized folders

### Command Line Usage

For advanced users or automation, you can use the command line interface:

```bash
python photo_cleaner.py --input /path/to/photos --threshold 0.7
```

### Command Line Options

- `--input` or `-i`: Input directory containing photos to scan (required)
- `--threshold` or `-t`: NSFW sensitivity threshold (0.0-1.0, default: 0.7)
- `--output` or `-o`: Output directory for organized photos (default: current directory)
- `--dry-run`: Preview what would be moved without actually moving files
- `--verbose` or `-v`: Enable detailed logging

### Examples

```bash
# Scan photos with default 70% threshold
python photo_cleaner.py -i "C:\Photos\Vacation"

# Use stricter 50% threshold
python photo_cleaner.py -i "C:\Photos" -t 0.5

# Preview mode (no files moved)
python photo_cleaner.py -i "C:\Photos" --dry-run

# Verbose output with custom output directory
python photo_cleaner.py -i "C:\Photos" -o "C:\Organized" -v
```

## How It Works

1. **Scanning**: The script recursively scans the input directory for image files
2. **Analysis**: Each image is processed through the OpenNSFW2 neural network
3. **Classification**: Images receive a confidence score (0-1) for NSFW content
4. **Organization**: Images exceeding the threshold are moved to `sensitive_photos/` folder
5. **Logging**: All operations are logged with timestamps and confidence scores

## Output Structure

```
Input Directory/
├── clean_photos/          # Photos below threshold
├── sensitive_photos/      # Photos above threshold
├── photo_cleaner.log      # Operation log
└── scan_report.txt        # Summary report
```

## GUI Application

The Photo Cleaner GUI provides a user-friendly interface with the following features:

- **Simple Navigation**: Easy directory selection with browse buttons
- **Visual Controls**: Slider for adjusting sensitivity threshold
- **Real-time Feedback**: Progress bar and detailed log display
- **Multiple Modes**: Switch between simple and advanced detection
- **Safety Features**: Dry run mode to preview without moving files
- **Result Access**: Quick buttons to open reports and output folders

## Model Information

This tool uses the OpenNSFW2 model, which is:
- Based on ResNet-50 architecture
- Trained on a large dataset of labeled images
- Provides confidence scores from 0 (safe) to 1 (NSFW)
- More accurate than the original Yahoo OpenNSFW model

## Privacy and Security

- **Local Processing**: All analysis is performed locally on your machine
- **No Data Transmission**: Images are never sent to external servers
- **Reversible Operations**: Original file structure can be restored from logs
- **Safe Defaults**: Conservative thresholds to minimize false positives

## Troubleshooting

### Common Issues

1. **Model Download Fails**: Ensure internet connection for initial model download
2. **Memory Errors**: Reduce batch size for large images or limited RAM
3. **Permission Errors**: Run with appropriate file system permissions
4. **Unsupported Formats**: Check that images are in supported formats (JPG, PNG, etc.)
5. **GUI Issues**: Make sure all required packages are installed (`pip install -r requirements.txt`)

### Performance Tips

- Use SSD storage for faster processing
- Close other applications to free up RAM
- Process smaller batches for very large collections
- For large libraries, use the command line version for better performance
