import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image
import numpy as np
import cv2

class DCTSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DCT Steganography")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="DCT Steganography", font=("Arial", 16))
        self.label.pack(pady=10)

        self.encode_button = tk.Button(root, text="Encode Message", command=self.encode_message)
        self.encode_button.pack(pady=5)

        self.decode_button = tk.Button(root, text="Decode Message", command=self.decode_message)
        self.decode_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=5)

    def encode_message(self):
        image_path = filedialog.askopenfilename(title="Select an Image to Encode")
        if not image_path:
            return

        message = simpledialog.askstring("Input", "Enter the message to encode:")
        if not message:
            return

        try:
            image = cv2.imread(image_path)
            stego_image = self.dct_encode(image, message)

            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                cv2.imwrite(save_path, stego_image)
                messagebox.showinfo("Success", "Message encoded and image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decode_message(self):
        image_path = filedialog.askopenfilename(title="Select an Image to Decode")
        if not image_path:
            return

        try:
            image = cv2.imread(image_path)
            decoded_message = self.dct_decode(image)
            messagebox.showinfo("Decoded Message", f"The decoded message is: {decoded_message}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def dct_encode(self, image, message):
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)

        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        binary_message += '1111111111111110'  # End delimiter

        # Convert to float for DCT
        y_float = np.float32(y)
        dct_coeff = cv2.dct(y_float)
        
        flat_dct = dct_coeff.flatten()
        message_index = 0

        for i in range(100, len(flat_dct), 50):  # Use mid-range frequencies
            if message_index < len(binary_message):
                bit = int(binary_message[message_index])
                flat_dct[i] += (-0.02 if bit == 0 else 0.02)  # Embed bit
                message_index += 1
            else:
                break

        dct_coeff = np.reshape(flat_dct, dct_coeff.shape)
        y_stego = cv2.idct(dct_coeff)
        y_stego = np.uint8(np.clip(y_stego, 0, 255))

        stego_image = cv2.merge((y_stego, cr, cb))
        stego_image = cv2.cvtColor(stego_image, cv2.COLOR_YCrCb2BGR)
        return stego_image

    def dct_decode(self, image):
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y, _, _ = cv2.split(ycrcb)
        
        y_float = np.float32(y)
        dct_coeff = cv2.dct(y_float)
        flat_dct = dct_coeff.flatten()
        
        binary_message = ''
        for i in range(100, len(flat_dct), 50):
            bit = '1' if flat_dct[i] > 0 else '0'
            binary_message += bit
            if binary_message[-16:] == '1111111111111110':
                break

        message = ''
        for i in range(0, len(binary_message) - 16, 8):
            message += chr(int(binary_message[i:i+8], 2))
        
        return message

if __name__ == "__main__":
    root = tk.Tk()
    app = DCTSteganographyApp(root)
    root.mainloop()
