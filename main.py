import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from railfane import decrypt, encrypt  # Import the railfance module

def text_to_binary(text):
    binary = ''.join(format(ord(char), '08b') for char in text)
    return binary

def binary_to_text(binary):
    text = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    return text

MARKER_TEXT = "###MARKER###"
MARKER = text_to_binary(MARKER_TEXT)

def encode_text_in_image():
    input_image_path = filedialog.askopenfilename(title="Select Input Image")
    if not input_image_path:
        return

    img = Image.open(input_image_path)
    img_data = list(img.getdata())

    # Check if the marker is already present in the image
    binary_data = ''.join([str(pixel[i] & 1) for pixel in img_data for i in range(3)])
    if MARKER in binary_data:
        messagebox.showwarning("Warning", "This Photo Has a Secret Message.")
        return

    text_to_hide = entry_text.get("1.0", "end-1c")
    try:
        key = int(entry_key.get())
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid key.")
        return

    if not text_to_hide:
        messagebox.showwarning("Warning", "Please enter text to hide.")
        return

    output_image_path = filedialog.asksaveasfilename(title="Save Output Image", defaultextension=".png")
    if not output_image_path:
        return

    enc = encrypt(text_to_hide, key)  # Encrypt the text
    binary_text = text_to_binary(enc)

    # Add end marker
    binary_text += MARKER

    data_index = 0
    img_data = list(img.getdata())

    encoded_pixels = []
    for pixel in img_data:
        if data_index < len(binary_text):
            pixel = list(pixel)
            for i in range(3):  # RGB channels
                if data_index < len(binary_text):
                    if binary_text[data_index] == '1':
                        pixel[i] |= 1  # Set the least significant bit to 1
                    else:
                        pixel[i] &= ~1  # Set the least significant bit to 0
                    data_index += 1
            encoded_pixels.append(tuple(pixel))
        else:
            encoded_pixels.append(pixel)

    img.putdata(encoded_pixels)
    img.save(output_image_path)
    messagebox.showinfo("Success", "Text encoded successfully!")

def decode_text_from_image():
    input_image_path = filedialog.askopenfilename(title="Select Image with Hidden Text")
    if not input_image_path:
        return
    
    img = Image.open(input_image_path)
    img_data = list(img.getdata())

    binary_text = ""
    char = ""
    try:
        key = int(entry_key.get())
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid key.")
        return

    end_marker_found = False  # Flag to indicate if end marker is found
    for pixel in img_data:
        if end_marker_found:
            break
        for i in range(3):  # RGB channels
            char += str(pixel[i] & 1)
            if len(char) == 8:
                binary_text += char
                char = ""
                # Check if the end marker is found
                if binary_text[-len(MARKER):] == MARKER:
                    end_marker_found = True
                    binary_text = binary_text[:-len(MARKER)]  # Remove the end marker from binary text
                    break

    if end_marker_found:
        decoded_text = binary_to_text(binary_text)  # Decrypt the text
        messagebox.showinfo("Message Before Decrypt", decoded_text)
        decoded_text = decrypt(binary_to_text(binary_text), key)  # Decrypt the text
        messagebox.showinfo("original Message", decoded_text)
    else:
        messagebox.showinfo("No Secret Message", "No secret message found in the image.")

# GUI Setup
root = tk.Tk()
root.title("Steganography Tool")

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

label_text = tk.Label(frame_input, text="Enter text to hide:")
label_text.pack()

entry_text = tk.Text(frame_input, height=4, width=50)
entry_text.pack()

frame_input1 = tk.Frame(root)
frame_input1.pack(pady=10)

label_key = tk.Label(frame_input1, text="Enter Key:")
label_key.pack()

entry_key = tk.Entry(frame_input1, width=10)
entry_key.pack()

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)

button_encode = tk.Button(frame_buttons, text="Encode Text in Image", command=encode_text_in_image)
button_encode.grid(row=0, column=0, padx=5)

button_decode = tk.Button(frame_buttons, text="Decode Text from Image", command=decode_text_from_image)
button_decode.grid(row=0, column=1, padx=5)

root.mainloop()
