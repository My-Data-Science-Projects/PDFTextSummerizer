import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from pdf2image import convert_from_path
import easyocr
from transformers import pipeline
import torch

POPPLER_PATH = r"C:\poppler_ocr\Library\bin"

# ========== GPU Check ==========
device = 0 if torch.cuda.is_available() else -1
print("Using GPU" if device == 0 else "Using CPU")

# ========== Hugging Face Summarizer ==========
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

# ========== EasyOCR Reader ==========
reader = easyocr.Reader(['en'], gpu=(device == 0))

# ========== PDF to Text ==========
def extract_text_from_pdf(pdf_path):
    try:
        # pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH) # If POPPLER_PATH not asigned in System Environment Variable
        pages = convert_from_path(pdf_path)
    except Exception as e:
        messagebox.showerror("PDF Error", f"Could not read PDF: {e}")
        return ""
    
    full_text = ""
    for i, page in enumerate(pages):
        image_path = f"temp_page_{i}.jpg"
        page.save(image_path, 'JPEG')
        result = reader.readtext(image_path, detail=0, paragraph=True)
        full_text += "\n".join(result) + "\n\n"
        os.remove(image_path)  # Cleanup
    return full_text.strip()

# ========== GUI Callbacks ==========
def choose_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        summary_output.delete(1.0, tk.END)
        summary_output.insert(tk.END, "Extracting and summarizing text, please wait...\n\n")
        app.update_idletasks()

        extracted = extract_text_from_pdf(file_path)
        if not extracted:
            summary_output.insert(tk.END, "No readable text found in PDF.")
            return

        try:
            chunks = [extracted[i:i+1024] for i in range(0, len(extracted), 1024)]
            summarized = []
            for chunk in chunks:
                summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
                summarized.append(summary)
            final_summary = "\n".join(summarized)
        except Exception as e:
            summary_output.delete(1.0, tk.END)
            summary_output.insert(tk.END, f"Summarization failed: {e}")
            return

        summary_output.delete(1.0, tk.END)
        summary_output.insert(tk.END, final_summary)
        global latest_summary
        latest_summary = final_summary

def save_txt():
    if not latest_summary:
        messagebox.showwarning("No Summary", "Please summarize a PDF first.")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(latest_summary)
        messagebox.showinfo("Saved", f"Summary saved to:\n{save_path}")

# ========== GUI Layout ==========
app = tk.Tk()
app.title("AI PDF Summarizer")
app.geometry("900x650")
app.resizable(False, False)

title_label = tk.Label(app, text="📄 AI PDF Summarizer", font=("Helvetica", 18, "bold"))
title_label.pack(pady=10)

tk.Button(app, text="📂 Select PDF", command=choose_pdf, font=("Helvetica", 12)).pack(pady=10)

summary_output = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=110, height=28, font=("Consolas", 10))
summary_output.pack(padx=10, pady=5)

tk.Button(app, text="💾 Download Summary as .txt", command=save_txt, font=("Helvetica", 12)).pack(pady=10)

latest_summary = ""

app.mainloop()
