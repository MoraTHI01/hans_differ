#!/usr/bin/env python
"""Video processing utilities for HAnS upload system"""
__author__ = "HAnS Development Team"
__copyright__ = "Copyright 2024, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Production"

import os
import json
import subprocess
import tempfile
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing operations including aspect ratio checking and conversion"""

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def check_aspect_ratio(self, video_path: str) -> Dict[str, any]:
        """
        Check video aspect ratio using ffprobe

        Args:
            video_path: Path to the video file

        Returns:
            Dict containing aspect ratio information and whether conversion is needed
        """
        try:
            # Run ffprobe to get video stream information
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=sample_aspect_ratio,display_aspect_ratio,width,height',
                '-of', 'json',
                video_path
            ]

            logger.info(f"Checking aspect ratio for: {video_path}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse JSON output
            probe_data = json.loads(result.stdout)

            if not probe_data.get('streams'):
                return {
                    'success': False,
                    'error': 'No video streams found',
                    'needs_conversion': False
                }

            stream = probe_data['streams'][0]
            sample_aspect_ratio = stream.get('sample_aspect_ratio', 'N/A')
            display_aspect_ratio = stream.get('display_aspect_ratio', 'N/A')
            width = stream.get('width', 0)
            height = stream.get('height', 0)

            # Check if aspect ratio needs fixing
            needs_conversion = self._needs_aspect_ratio_conversion(
                sample_aspect_ratio, display_aspect_ratio, width, height
            )

            return {
                'success': True,
                'sample_aspect_ratio': sample_aspect_ratio,
                'display_aspect_ratio': display_aspect_ratio,
                'width': width,
                'height': height,
                'needs_conversion': needs_conversion
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"ffprobe failed: {e.stderr}")
            return {
                'success': False,
                'error': f'ffprobe failed: {e.stderr}',
                'needs_conversion': False
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output: {e}")
            return {
                'success': False,
                'error': f'Failed to parse ffprobe output: {e}',
                'needs_conversion': False
            }
        except Exception as e:
            logger.error(f"Unexpected error checking aspect ratio: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {e}',
                'needs_conversion': False
            }

    def _needs_aspect_ratio_conversion(self, sample_aspect_ratio: str, display_aspect_ratio: str,
                                     width: int, height: int) -> bool:
        """
        Determine if video needs aspect ratio conversion

        Args:
            sample_aspect_ratio: Sample aspect ratio from ffprobe
            display_aspect_ratio: Display aspect ratio from ffprobe
            width: Video width
            height: Video height

        Returns:
            True if conversion is needed, False otherwise
        """
        # Check for common aspect ratio issues
        if sample_aspect_ratio == 'N/A' or display_aspect_ratio == 'N/A':
            return True

        # Check if sample aspect ratio is not 1:1 (square pixels)
        if sample_aspect_ratio != '1:1':
            return True

        # Check for common problematic aspect ratios
        problematic_ratios = ['0:1', 'N/A', 'unknown']
        if sample_aspect_ratio in problematic_ratios or display_aspect_ratio in problematic_ratios:
            return True

        # Check if dimensions suggest non-standard aspect ratio
        if width > 0 and height > 0:
            calculated_ratio = width / height
            # Check if ratio is close to standard ratios (16:9, 4:3, etc.)
            standard_ratios = [16/9, 4/3, 1.0]  # 16:9, 4:3, 1:1
            tolerance = 0.1

            for std_ratio in standard_ratios:
                if abs(calculated_ratio - std_ratio) < tolerance:
                    return False

            # If not close to any standard ratio, might need conversion
            return True

        return False

    def convert_video(self, input_path: str, output_path: str) -> Dict[str, any]:
        """
        Convert video to proper format with correct aspect ratio

        Args:
            input_path: Path to input video file
            output_path: Path for output video file

        Returns:
            Dict containing conversion result information
        """
        try:
            logger.info(f"Converting video: {input_path} -> {output_path}")

            # FFmpeg command to fix aspect ratio and convert to proper format
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', 'scale=3840:2160,setsar=1',
                '-c:v', 'libx264',
                '-crf', '18',
                '-preset', 'slow',
                '-y',  # Overwrite output file
                output_path
            ]

            # Run conversion with progress logging
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Monitor progress (simplified - in production you might want more detailed progress)
            stdout, stderr = process.communicate()
            logger.info(f"FFmpeg stdout: {stdout}")
            logger.info(f"FFmpeg stderr: {stderr}")
            logger.info(f"FFmpeg return code: {process.returncode}")

            if process.returncode == 0:
                # Check if output file was created and has reasonable size
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Video conversion successful: {output_path}")
                    return {
                        'success': True,
                        'output_path': output_path,
                        'message': 'Video converted successfully'
                    }
                else:
                    logger.error("Conversion completed but output file is missing or empty")
                    return {
                        'success': False,
                        'error': 'Output file is missing or empty',
                        'stderr': stderr
                    }
            else:
                logger.error(f"FFmpeg conversion failed: {stderr}")
                return {
                    'success': False,
                    'error': f'FFmpeg conversion failed: {stderr}',
                    'stderr': stderr
                }

        except Exception as e:
            logger.error(f"Unexpected error during video conversion: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {e}'
            }

    def process_video_file(self, file_stream, filename: str) -> Tuple[bool, str, str]:
        """
        Process a video file: check aspect ratio and convert if needed

        Args:
            file_stream: File stream object from Flask
            filename: Original filename

        Returns:
            Tuple of (success, processed_file_path, message)
        """
        temp_input_path = None
        temp_output_path = None

        try:
            # Create temporary files
            temp_input_path = os.path.join(self.temp_dir, f"input_{filename}")
            temp_output_path = os.path.join(self.temp_dir, f"output_{filename}")

            # Save uploaded file to temporary location
            file_stream.seek(0)  # Reset stream position
            with open(temp_input_path, 'wb') as temp_file:
                temp_file.write(file_stream.read())

            logger.info(f"Saved uploaded file to: {temp_input_path}")
            logger.info(f"File size: {os.path.getsize(temp_input_path)} bytes")

            # Check aspect ratio
            aspect_check = self.check_aspect_ratio(temp_input_path)

            if not aspect_check['success']:
                return False, temp_input_path, f"Aspect ratio check failed: {aspect_check['error']}"

            if aspect_check['needs_conversion']:
                logger.info("Video needs aspect ratio conversion")
                
                # Convert video
                conversion_result = self.convert_video(temp_input_path, temp_output_path)
                
                if conversion_result['success']:
                    # Clean up input file but keep output file for upload
                    if os.path.exists(temp_input_path):
                        os.remove(temp_input_path)
                    
                    logger.info(f"Video conversion successful. Output file: {temp_output_path}")
                    logger.info(f"Output file size: {os.path.getsize(temp_output_path)} bytes")
                    return True, temp_output_path, "Video converted to proper format"
                else:
                    return False, temp_input_path, f"Conversion failed: {conversion_result['error']}"
            else:
                logger.info("Video aspect ratio is correct, no conversion needed")
                return True, temp_input_path, "Video format is already correct"

        except Exception as e:
            logger.error(f"Error processing video file: {e}")
            return False, temp_input_path or "", f"Processing error: {e}"

        finally:
            # Clean up temporary files on error only
            # Note: We don't clean up temp_output_path here as it might be needed for upload
            if temp_input_path and os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except:
                    pass


# Global instance
video_processor = VideoProcessor()
