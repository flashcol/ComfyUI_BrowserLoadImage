"""
Tests for Browser Load Image nodes
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

from nodes.browser_load_image import BrowserLoadImage

class TestBrowserLoadImage(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_images_dir = Path(self.temp_dir) / "input"
        self.test_images_dir.mkdir()
        
        # Create some test images
        self.create_test_images()
        
        # Create node instance
        self.node = BrowserLoadImage()
        self.node.input_folder = self.test_images_dir
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_images(self):
        """Create test image files"""
        from PIL import Image
        
        # Create a simple test image
        test_image = Image.new('RGB', (512, 512), color='red')
        
        # Save test images
        test_image.save(self.test_images_dir / "test1.jpg")
        test_image.save(self.test_images_dir / "test2.png")
        test_image.save(self.test_images_dir / "test3.webp")
        
        # Create a subdirectory with images
        subdir = self.test_images_dir / "subdir"
        subdir.mkdir()
        test_image.save(subdir / "test4.jpg")
    
    def test_input_types(self):
        """Test INPUT_TYPES method"""
        input_types = BrowserLoadImage.INPUT_TYPES()
        
        self.assertIn("required", input_types)
        self.assertIn("image", input_types["required"])
        self.assertIn("hidden", input_types)
        self.assertIn("node_id", input_types["hidden"])
    
    def test_return_types(self):
        """Test RETURN_TYPES and RETURN_NAMES"""
        self.assertEqual(BrowserLoadImage.RETURN_TYPES, ("IMAGE", "MASK"))
        self.assertEqual(BrowserLoadImage.RETURN_NAMES, ("image", "mask"))
    
    def test_category(self):
        """Test CATEGORY"""
        self.assertEqual(BrowserLoadImage.CATEGORY, "image")
    
    def test_scan_images(self):
        """Test image scanning functionality"""
        self.node._scan_images()
        
        # Should find all test images
        self.assertEqual(len(self.node.image_list), 4)
        
        # Check image info
        image_info = self.node.image_list[0]
        self.assertIn('filename', image_info)
        self.assertIn('path', image_info)
        self.assertIn('size', image_info)
        self.assertIn('width', image_info)
        self.assertIn('height', image_info)
    
    def test_get_image_list_pagination(self):
        """Test image list pagination"""
        self.node._scan_images()
        
        # Test first page
        result = self.node.get_image_list(page=1, per_page=2)
        self.assertEqual(len(result['images']), 2)
        self.assertEqual(result['pagination']['current_page'], 1)
        self.assertEqual(result['pagination']['total_pages'], 2)
        self.assertTrue(result['pagination']['has_next'])
        self.assertFalse(result['pagination']['has_prev'])
        
        # Test second page
        result = self.node.get_image_list(page=2, per_page=2)
        self.assertEqual(len(result['images']), 2)
        self.assertEqual(result['pagination']['current_page'], 2)
        self.assertEqual(result['pagination']['total_pages'], 2)
        self.assertFalse(result['pagination']['has_next'])
        self.assertTrue(result['pagination']['has_prev'])
    
    def test_get_image_list_search(self):
        """Test image list search functionality"""
        self.node._scan_images()
        
        # Search for specific filename
        result = self.node.get_image_list(search="test1")
        self.assertEqual(len(result['images']), 1)
        self.assertEqual(result['images'][0]['filename'], 'test1.jpg')
        
        # Search with no results
        result = self.node.get_image_list(search="nonexistent")
        self.assertEqual(len(result['images']), 0)
    
    def test_get_thumbnail(self):
        """Test thumbnail generation"""
        self.node._scan_images()
        
        if self.node.image_list:
            image_path = self.node.image_list[0]['path']
            thumbnail = self.node.get_thumbnail(image_path)
            
            self.assertIsNotNone(thumbnail)
            self.assertIsInstance(thumbnail, str)
            # Should be base64 encoded
            self.assertTrue(len(thumbnail) > 0)
    
    def test_get_image_metadata(self):
        """Test image metadata extraction"""
        self.node._scan_images()
        
        if self.node.image_list:
            image_path = self.node.image_list[0]['path']
            metadata = self.node.get_image_metadata(image_path)
            
            self.assertIsNotNone(metadata)
            self.assertIn('filename', metadata)
            self.assertIn('width', metadata)
            self.assertIn('height', metadata)
            self.assertIn('size', metadata)
    
    def test_load_image(self):
        """Test image loading"""
        self.node._scan_images()
        
        if self.node.image_list:
            image_info = self.node.image_list[0]
            
            # Test loading by dict
            try:
                import torch
                image_tensor, mask_tensor = self.node.load_image(image_info)
                
                self.assertIsInstance(image_tensor, torch.Tensor)
                self.assertIsInstance(mask_tensor, torch.Tensor)
                
                # Check tensor dimensions (should be [1, H, W, C])
                self.assertEqual(len(image_tensor.shape), 4)
                self.assertEqual(image_tensor.shape[0], 1)  # Batch size
                
            except ImportError:
                # Skip test if torch is not available
                pass
    
    def test_refresh_images(self):
        """Test image refresh functionality"""
        # Initial scan
        self.node._scan_images()
        initial_count = len(self.node.image_list)
        
        # Add a new image
        from PIL import Image
        new_image = Image.new('RGB', (256, 256), color='blue')
        new_image.save(self.test_images_dir / "new_test.jpg")
        
        # Refresh
        self.node.refresh_images()
        
        # Should find the new image
        self.assertEqual(len(self.node.image_list), initial_count + 1)
        
        # Check that new image is in the list
        filenames = [img['filename'] for img in self.node.image_list]
        self.assertIn('new_test.jpg', filenames)

if __name__ == '__main__':
    unittest.main()