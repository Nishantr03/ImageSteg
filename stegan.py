from tkinter import Tk, Label, Button, filedialog, Entry, messagebox, Frame
from PIL import Image
import os

# Encryption/Decryption Functions
def encrypt_message(message, shift=3):
    return ''.join(chr((ord(char) - 32 + shift) % 95 + 32) for char in message)

def decrypt_message(encrypted_message, shift=3):
    return ''.join(chr((ord(char) - 32 - shift) % 95 + 32) for char in encrypted_message)

# Encoding Function
def encode_image(image_path, message):
    encrypted_message = encrypt_message(message)
    img = Image.open(image_path)

    binary_message = ''.join(format(ord(char), '08b') for char in encrypted_message) + '11111111'

    if len(binary_message) > img.width * img.height * 3:
        raise ValueError("Message is too large for the image")

    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(img.getpixel((x, y)))

            for i in range(3):
                if data_index < len(binary_message):
                    pixel[i] = pixel[i] & ~1 | int(binary_message[data_index])
                    data_index += 1

            img.putpixel((x, y), tuple(pixel))

    encoded_path = 'encoded_image.png'
    img.save(encoded_path)
    return encoded_path

# Decoding Function
def decode_image(image_path):
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    binary_message = ''
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            for i in range(3):  # Extract LSBs of RGB components
                binary_message += str(pixel[i] & 1)

    # Check if the delimiter exists
    if '11111111' not in binary_message:
        raise ValueError("No hidden data found in the image")

    # Extract binary data up to the delimiter
    binary_message = binary_message.split('11111111')[0]

    # Convert binary data to text
    try:
        message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8))
    except ValueError:
        raise ValueError("Error decoding binary message. Data might be corrupt or incomplete.")

    return decrypt_message(message)

# Steganalysis Function
def detect_hidden_data(image_path):
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    binary_message = ''
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            for i in range(3):  # Extract LSBs of RGB components
                binary_message += str(pixel[i] & 1)

    # Check for the delimiter `11111111` in binary message
    if '11111111' in binary_message:
        return True
    return False

# GUI Functions
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    return file_path

def encode_gui():
    file_path = select_file()
    if not file_path:
        return
    message = message_entry.get()
    if not message:
        messagebox.showwarning("Error", "Please enter a message to encode!")
        return
    try:
        encoded_path = encode_image(file_path, message)
        messagebox.showinfo("Success", f"Message encoded! Saved as {encoded_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def decode_gui():
    file_path = select_file()
    if not file_path:
        return
    try:
        decoded_message = decode_image(file_path)
        messagebox.showinfo("Decoded Message", f"Decoded Message: {decoded_message}")
    except ValueError as ve:
        messagebox.showwarning("Decoding Failed", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

def steganalysis_gui():
    file_path = select_file()
    if not file_path:
        return
    try:
        hidden_data_present = detect_hidden_data(file_path)
        if hidden_data_present:
            messagebox.showinfo("Steganalysis Result", "Hidden data is present in this image.")
        else:
            messagebox.showinfo("Steganalysis Result", "No hidden data found in this image.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Layout
def setup_gui():
    root = Tk()
    root.title("Image Steganography Tool")
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
    Button(root, text="Detect Hidden Data", font=("Helvetica", 12), bg="#e67e22", fg="#ffffff", command=steganalysis_gui).pack(pady=10)

    # Footer
    footer = Label(root, text="Developed by Nishant", font=("Helvetica", 10), bg="#34495e", fg="#ecf0f1", pady=5)
    footer.pack(side="bottom", fill="x")

    root.mainloop()

# Run the GUI
setup_gui()
