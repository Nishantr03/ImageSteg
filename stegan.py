from tkinter import Tk, Label, Button, filedialog, Entry, messagebox, Frame
import numpy as np
import cv2

# 🔹 Encrypt & Decrypt Functions
def encrypt_message(message, shift=3):
    return ''.join(chr((ord(char) - 32 + shift) % 95 + 32) for char in message)

def decrypt_message(encrypted_message, shift=3):
    return ''.join(chr((ord(char) - 32 - shift) % 95 + 32) for char in encrypted_message)

# 🔹 Convert text to binary
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

# 🔹 Convert binary to text
def binary_to_text(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

# 🔹 **DCT Encoding Function (Fixed & Debugged)**
def encode_image_dct(image_path, message):
    encrypted_message = encrypt_message(message) + '###'  # Append delimiter
    binary_message = text_to_binary(encrypted_message)

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    if len(binary_message) > (h * w) // 64:
        raise ValueError("Message too large to encode in this image")

    print(f"🔹 Encoding {len(binary_message)} bits into image of size {h}x{w}")

    idx = 0
    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            if idx >= len(binary_message):
                break

            block = np.float32(img[i:i+8, j:j+8])
            dct_block = cv2.dct(block)

            bit = int(binary_message[idx])
            coeff = dct_block[4, 4]

            # 🔹 More Reliable Bit Embedding
            new_coeff = int(np.round(coeff))
            if bit == 1:
                new_coeff |= 1  # Set LSB to 1
            else:
                new_coeff &= ~1  # Set LSB to 0

            dct_block[4, 4] = float(new_coeff)  # Convert back to float
            img[i:i+8, j:j+8] = cv2.idct(dct_block)
            idx += 1

    encoded_path = 'encoded_dct_image.png'
    cv2.imwrite(encoded_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])  # Lossless PNG
    print(f"✅ Encoding complete. Saved as {encoded_path}")
    return encoded_path

# 🔹 **DCT Decoding Function (Fully Debugged)**
def decode_image_dct(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape
    binary_message = ""
    max_bits = (h * w) // 64  # Max possible bits to prevent infinite loop

    print(f"🔹 Decoding image of size {h}x{w}")

    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            block = np.float32(img[i:i+8, j:j+8])
            dct_block = cv2.dct(block)

            coeff = dct_block[4, 4]
            extracted_bit = int(np.round(coeff)) & 1  # Extract LSB
            binary_message += str(extracted_bit)

            # 🔹 Debugging: Print every 8-bit chunk
            if len(binary_message) % 8 == 0:
                last_char = binary_to_text(binary_message[-8:])
                print(f"Extracted Bits: {binary_message[-8:]} -> '{last_char}'")

                extracted_text = binary_to_text(binary_message)
                if "###" in extracted_text:
                    extracted_text = extracted_text.split("###")[0]
                    print(f"✅ Decoded Binary: {binary_message}")
                    print(f"✅ Decoded Encrypted Text: {extracted_text}")
                    return decrypt_message(extracted_text)

            # 🔹 Prevent Infinite Loop
            if len(binary_message) > max_bits:
                print("❌ Stopping: Exceeded max expected bits")
                break

    return "Decoding failed: No valid message found."

# 🔹 GUI Functions
def select_file():
    return filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])


def encode_gui():
    file_path = select_file()
    if not file_path:
        return
    message = message_entry.get()
    if not message:
        messagebox.showwarning("Error", "Please enter a message to encode!")
        return
    try:
        encoded_path = encode_image_dct(file_path, message)
        messagebox.showinfo("Success", f"Message encoded! Saved as {encoded_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decode_gui():
    file_path = select_file()
    if not file_path:
        return
    try:
        decoded_message = decode_image_dct(file_path)
        messagebox.showinfo("Decoded Message", f"Decoded Message: {decoded_message}")
    except ValueError as ve:
        messagebox.showwarning("Decoding Failed", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")


# 🔹 GUI Layout
def setup_gui():
    root = Tk()
    root.title("DCT-Based Image Steganography Tool")
    root.geometry("500x450")
    root.resizable(False, False)

    # Header
    header = Label(root, text="Image Steganography", font=("Helvetica", 18, "bold"), fg="#ffffff", bg="#2c3e50", pady=10)
    header.pack(fill="x")

    # Message Frame
    frame = Frame(root, padx=20, pady=20)
    frame.pack()

    Label(frame, text="Enter your secret message:", font=("Helvetica", 12)).grid(row=0, column=0, pady=10, sticky="w")
    global message_entry
    message_entry = Entry(frame, width=40, font=("Helvetica", 12))
    message_entry.grid(row=1, column=0, pady=5, sticky="w")

    # Buttons
    Button(root, text="Encode Message", font=("Helvetica", 12), bg="#3498db", fg="#ffffff", command=encode_gui).pack(pady=10)
    Button(root, text="Decode Message", font=("Helvetica", 12), bg="#2ecc71", fg="#ffffff", command=decode_gui).pack(pady=10)

    # Footer
    footer = Label(root, text="Developed by Nishant", font=("Helvetica", 10), bg="#34495e", fg="#ecf0f1", pady=5)
    footer.pack(side="bottom", fill="x")

    root.mainloop()


# 🔹 Run the GUI
setup_gui()