#11
import os
import cv2
import numpy as np
from bitarray import bitarray

class DCTSteganography:
    @staticmethod
    def dct_encode(image, message):
        # Convert message to binary with 16-bit length header
        ba = bitarray()
        ba.frombytes(message.encode('utf-8'))
        binary_data = ba.tolist()
        msg_len = [int(b) for b in format(len(binary_data), '016b')]
        binary_data = msg_len + binary_data
        
        # Convert to YCrCb and work on Y channel
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        block_size = 8
        h, w = y.shape
        data_index = 0
        
        # Calculate available blocks
        available_blocks = (h // block_size) * (w // block_size)
        needed_blocks = len(binary_data)
        
        if needed_blocks > available_blocks:
            raise ValueError(f"Message too large. Needs {needed_blocks} blocks, only {available_blocks} available")
        
        # Use multiple coefficients per block to increase capacity
        coeff_positions = [(1,2), (2,1), (3,1), (2,2)]  # Good mid-frequency positions
        
        for i in range(0, h - block_size + 1, block_size):
            for j in range(0, w - block_size + 1, block_size):
                if data_index >= len(binary_data):
                    break
                
                block = y[i:i+block_size, j:j+block_size].astype(np.float32)
                dct_block = cv2.dct(block)
                
                # Embed in multiple coefficients per block
                for pos in coeff_positions:
                    if data_index >= len(binary_data):
                        break
                    
                    coeff = dct_block[pos]
                    if binary_data[data_index]:
                        dct_block[pos] = coeff + 2.0 if coeff >= 0 else coeff - 2.0
                    else:
                        dct_block[pos] = coeff - 2.0 if coeff >= 0 else coeff + 2.0
                    data_index += 1
                
                idct_block = cv2.idct(dct_block)
                y[i:i+block_size, j:j+block_size] = np.clip(idct_block, 0, 255)
        
        stego_image = cv2.merge((y, cr, cb))
        return cv2.cvtColor(stego_image, cv2.COLOR_YCrCb2BGR)

    @staticmethod
    def dct_decode(image):
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, _, _ = cv2.split(ycrcb)
        
        block_size = 8
        h, w = y.shape
        data = bitarray()
        
        # Same coefficient positions as encoding
        coeff_positions = [(1,2), (2,1), (3,1), (2,2)]
        
        # First read 16-bit length
        len_bits = []
        blocks_read = 0
        bits_needed = 16
        
        for i in range(0, h - block_size + 1, block_size):
            for j in range(0, w - block_size + 1, block_size):
                if len(len_bits) >= bits_needed:
                    break
                
                block = y[i:i+block_size, j:j+block_size].astype(np.float32)
                dct_block = cv2.dct(block)
                
                # Read from coefficients
                for pos in coeff_positions:
                    if len(len_bits) >= bits_needed:
                        break
                    
                    coeff = dct_block[pos]
                    len_bits.append(1 if abs(coeff) % 2.0 > 1.0 else 0)
        
        try:
            msg_len = int(''.join(map(str, len_bits)), 2)
        except:
            return "DECODING_ERROR_LENGTH"
        
        # Read message data
        data = bitarray()
        bits_read = 0
        
        for i in range(0, h - block_size + 1, block_size):
            for j in range(0, w - block_size + 1, block_size):
                if bits_read >= msg_len + bits_needed:
                    break
                
                block = y[i:i+block_size, j:j+block_size].astype(np.float32)
                dct_block = cv2.dct(block)
                
                for pos in coeff_positions:
                    if bits_read < bits_needed:
                        bits_read += 1
                        continue
                    if bits_read >= msg_len + bits_needed:
                        break
                    
                    coeff = dct_block[pos]
                    data.append(1 if abs(coeff) % 2.0 > 1.0 else 0)
                    bits_read += 1
        
        try:
            return data.tobytes().decode('utf-8')
        except:
            return "DECODING_ERROR_DATA"

def test_single_image():
    test_image_path = "images/20056.png"
    test_message = "Abundance"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    image = cv2.imread(test_image_path)
    if image is None:
        print("❌ Failed to load test image")
        return False
    
    print("\n=== Testing Parameters ===")
    print(f"Image dimensions: {image.shape[1]}x{image.shape[0]}")
    print(f"Original message: '{test_message}' (length: {len(test_message)} chars)")
    
    # Verify capacity
    block_size = 8
    available_bits = (image.shape[0]//block_size) * (image.shape[1]//block_size) * 4  # 4 coeffs/block
    needed_bits = 16 + len(test_message) * 8  # 16-bit header + message
    
    print(f"Available bits: {available_bits}, Needed bits: {needed_bits}")
    
    if needed_bits > available_bits:
        print(f"❌ Message too large for image. Try with shorter message or larger image.")
        return False
    
    # Encode
    try:
        encoded = DCTSteganography.dct_encode(image, test_message)
        cv2.imwrite("test_encoded.png", encoded, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("✅ Encoding completed")
    except Exception as e:
        print(f"❌ Encoding failed: {str(e)}")
        return False
    
    # Test memory decode
    mem_decoded = DCTSteganography.dct_decode(encoded)
    print(f"Memory decode: '{mem_decoded}'")
    
    # Test file decode
    file_decoded = DCTSteganography.dct_decode(cv2.imread("test_encoded.png"))
    print(f"File decode: '{file_decoded}'")
    
    # Verify
    if mem_decoded == test_message and file_decoded == test_message:
        print("✅ Test successful!")
        return True
    else:
        print("\n❌ Test failed - Debugging Info:")
        print(f"- Memory and file decodes match: {mem_decoded == file_decoded}")
        
        print("\n🛠️ Troubleshooting steps:")
        print("1. Try with a larger image (at least 200x200 pixels)")
        print("2. Try with a shorter test message (like 'test')")
        print("3. Check if the image is truecolor (not palette-based)")
        print("4. Try increasing the modulation value (currently 2.0) in dct_encode()")
        return False

if __name__ == "__main__":
    if test_single_image():
        print("\nTest successful! Ready to process all images.")
    else:
        print("\nPlease fix the test case before proceeding.")