DCT-Based Image Steganography
#2@
📌 Overview

This is a Discrete Cosine Transform (DCT) based Steganography Application built using Python and Tkinter. It allows users to:

Encode secret messages into an image using DCT.

Decode messages hidden within an image.

The application uses mid-frequency DCT coefficients to embed text data securely while minimizing visible distortions in the image.

🚀 Features

Text Encoding: Hide secret messages inside an image using DCT.

Text Decoding: Extract hidden messages from a stego image.

Simple GUI: Built using Tkinter for easy usage.

Lossless Extraction: Extracts the exact message without loss.

Supports PNG formats.

🛠️ Usage

1️⃣ Run the Application

Execute the following command in the terminal:

2️⃣ Encoding a Message

Click 'Select Image' to choose an image.

Enter the secret message in the text box.

Click 'Encode & Save' to embed the message into the image.

The stego-image will be saved with the hidden message.

3️⃣ Decoding a Message

Click 'Select Encoded Image' to open an image with hidden text.

Click 'Decode' to extract the message.

The extracted message will be displayed in a popup.
