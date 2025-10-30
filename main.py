from lzw import LZWCoder
import tkinter as tk
from tkinter import ttk

isReseted = 0


def toggleFields():
    if decodeVar.get():
        encodeEntry.config(state="disabled")
        decodeEntry.config(state="normal")
        phraseDropdown.config(state="disabled")
        customInput.config(state="disabled")
    else:
        encodeEntry.config(state="normal")
        decodeEntry.config(state="disabled")
        phraseDropdown.config(state="normal")
        if phraseVar.get() == "Custom":
            customInput.config(state="normal")
        else:
            customInput.config(state="disabled")


def custom(*args):
    if phraseVar.get() == "Custom":
        customInput.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        if not decodeVar.get():
            customInput.config(state="normal")
    else:
        customInput.grid_forget()


def updateResetPolicy(*args):
    global isReseted
    resetPolicyVal = resetPolicyVar.get()
    isReseted = int(resetPolicyVal.split()[0])


def buttonHandle():
    fileName = decodeEntry.get() if decodeVar.get() else encodeEntry.get()

    if phraseVar.get() == "Custom":
        custVal = customInput.get()
        phraseVal = int(custVal) if custVal.isdigit() else "Invalid"
        if phraseVal == "Invalid":
            exit()
    else:
        phraseVal = int(phraseVar.get().split()[0])

    print(f"File to process: {fileName}")
    print(f"Amount of phrases: {phraseVal}")

    if decodeVar.get():
        if not fileName:
            print("Error, please enter a file to decode.")
            return
        processFile(fileName, None, encode=False)
    else:
        if not fileName:
            print("Error, please enter a file to encode.")
            return
        processFile(fileName, "comp.bin", dictSize=phraseVal, encode=True)


def processFile(inputPath, outputPath, dictSize=256, encode=True):
    global isReseted
    coder = LZWCoder(dictSize)

    if encode:
        coder.encodeFile(inputPath, outputPath, isReseted)
    else:
        coder.decodeFile(inputPath, outputPath)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Encoder/Decoder")
    root.geometry("400x250")
    root.resizable(False, False)

    tk.Label(root, text="File to encode:").grid(
        row=0, column=0, sticky="w", padx=10, pady=5
    )
    encodeEntry = tk.Entry(root, width=30)
    encodeEntry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="File to decode:").grid(
        row=1, column=0, sticky="w", padx=10, pady=5
    )
    decodeEntry = tk.Entry(root, width=30, state="disabled")
    decodeEntry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Amount of phrases (2^bit=x):").grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    customInput = tk.Entry(root, width=10)
    customInput.grid_forget()

    phraseVar = tk.StringVar(value="256 (8-bit)")
    phraseVar.trace_add("write", custom)
    phraseDropdown = ttk.OptionMenu(
        root,
        phraseVar,
        "256 (8-bit)",
        "256 (8-bit)",
        "512 (9-bit)",
        "1024 (10-bit)",
        "2048 (11-bit)",
        "4096 (12-bit)",
        "8192 (13-bit)",
        "16384 (14-bit)",
        "32768 (15-bit)",
        "65536 (16-bit)",
        "Custom",
    )
    phraseDropdown.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    decodeVar = tk.BooleanVar(value=False)
    decodeCheck = tk.Checkbutton(
        root, text="Decode?", variable=decodeVar, command=toggleFields
    )
    decodeCheck.grid(row=4, column=0, columnspan=2, pady=5)

    resetPolicyVar = tk.StringVar(value="0 - on limit hit: freeze dictionary")
    resetPolicyVar.trace_add("write", updateResetPolicy)
    resetPolicyDropdown = ttk.OptionMenu(
        root,
        resetPolicyVar,
        "0 - on limit hit: freeze dictionary",
        "0 - on limit hit: freeze dictionary",
        "1 - on limit hit: reset the dictionary and build a new one",
        "2 - on limit hit: dynamically expand the dictionary",
    )
    resetPolicyDropdown.grid(row=5, column=0, columnspan=2, pady=5)

    actionButton = tk.Button(root, text="Run", command=buttonHandle)
    actionButton.grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()
