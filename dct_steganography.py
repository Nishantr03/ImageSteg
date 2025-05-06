import os
import cv2
import pandas as pd
import numpy as np


class DCTSteganography:
    @staticmethod
    def dct_encode(image, message):
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)

        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)

        # Add message length (16 bits = max 65535 bits = 8191 characters)
        msg_len = format(len(binary_message), '016b')
        binary_data = msg_len + binary_message

        y_float = np.float32(y)
        dct_coeff = cv2.dct(y_float)

        flat_dct = dct_coeff.flatten()
        message_index = 0

        for i in range(100, len(flat_dct), 1):  # Use more coefficients for more capacity
            if message_index < len(binary_data):
                bit = int(binary_data[message_index])
                if bit == 0:
                    flat_dct[i] = flat_dct[i] - abs(flat_dct[i]) % 0.02
                else:
                    flat_dct[i] = flat_dct[i] - abs(flat_dct[i]) % 0.02 + 0.01
                message_index += 1
            else:
                break

        dct_coeff = np.reshape(flat_dct, dct_coeff.shape)
        y_stego = cv2.idct(dct_coeff)
        y_stego = np.uint8(np.clip(y_stego, 0, 255))

        stego_image = cv2.merge((y_stego, cr, cb))
        stego_image = cv2.cvtColor(stego_image, cv2.COLOR_YCrCb2BGR)
        return stego_image

    @staticmethod
    def dct_decode(image):
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, _, _ = cv2.split(ycrcb)

        y_float = np.float32(y)
        dct_coeff = cv2.dct(y_float)
        flat_dct = dct_coeff.flatten()

        binary_data = ''
        for i in range(100, len(flat_dct), 1):
            remainder = abs(flat_dct[i]) % 0.02
            bit = '1' if 0.005 < remainder < 0.015 else '0'
            binary_data += bit

        # Read first 16 bits as message length
        msg_len = int(binary_data[:16], 2)

        # Extract actual message bits
        binary_message = binary_data[16:16 + msg_len]

        message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            if len(byte) == 8:
                message += chr(int(byte, 2))

        return message


def encode_all():
    df = pd.read_csv("messages.csv", encoding='utf-8')
    os.makedirs("encoded_images", exist_ok=True)

    for _, row in df.iterrows():
        image_path = f"images/{row['image_name']}"
        message = str(row['message'])

        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            encoded_image = DCTSteganography.dct_encode(image, message)
            save_path = f"encoded_images/{os.path.splitext(row['image_name'])[0]}.bmp"
            cv2.imwrite(save_path, encoded_image)
            print(f"✅ Encoded: {row['image_name']}")
        else:
            print(f"❌ Image not found: {row['image_name']}")


def decode_all():
    decoded_data = []
    os.makedirs("decoded_messages", exist_ok=True)

    for image_name in os.listdir("encoded_images"):
        image_path = f"encoded_images/{image_name}"
        image = cv2.imread(image_path)

        if image is not None:
            decoded_message = DCTSteganography.dct_decode(image)
            decoded_data.append([image_name, decoded_message])
            print(f"✅ Decoded: {image_name}")
        else:
            print(f"❌ Failed to load: {image_name}")

    df = pd.DataFrame(decoded_data, columns=["image_name", "decoded_message"])
    df.to_csv("decoded_messages.csv", index=False, encoding='utf-8')
    print("🎯 All decoded messages saved to decoded_messages.csv")


if __name__ == "__main__":
    encode_all()
    decode_all()
