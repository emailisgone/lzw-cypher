import os
import struct
import time
from collections import defaultdict


class LZWCoder:
    def __init__(self, dictSize=256):
        self.maxDictSize = dictSize

    def getUniqueFileName(self, baseName, extension):
        counter = 0
        while True:
            filename = f"{baseName}{counter if counter > 0 else ''}{extension}"
            if not os.path.exists(filename):
                return filename
            counter += 1

    def writeBits(self, value, numBits, bitBuffer, bitPosition):
        for i in range(numBits - 1, -1, -1):
            bit = (value >> i) & 1
            byteIndex = bitPosition >> 3
            bitInByte = 7 - (bitPosition & 7)

            while byteIndex >= len(bitBuffer):
                bitBuffer.append(0)

            if bit:
                bitBuffer[byteIndex] |= 1 << bitInByte
            bitPosition += 1
        return bitPosition

    def readBits(self, numBits, bitBuffer, bitPosition):
        value = 0
        for _ in range(numBits):
            byteIndex = bitPosition >> 3
            bitInByte = 7 - (bitPosition & 7)
            bit = (bitBuffer[byteIndex] >> bitInByte) & 1
            value = (value << 1) | bit
            bitPosition += 1
        return value, bitPosition

    def getBitLength(self, value):
        return max(value.bit_length(), 1)

    def encodeFile(self, inputPath, outputPath, resetPolicy):
        try:
            with open(inputPath, "rb") as file:
                data = file.read()

            startTime = time.time()
            originalSize = len(data)
            _, extension = os.path.splitext(inputPath)

            dictionary = {bytes([i]): i for i in range(256)}
            nextCode = 256

            outputCodes = []

            current = bytes([data[0]])
            for byte in data[1:]:
                nextByte = bytes([byte])
                currPlusNext = current + nextByte

                if currPlusNext in dictionary:
                    current = currPlusNext
                else:
                    outputCodes.append(dictionary[current])

                    if nextCode < self.maxDictSize:
                        dictionary[currPlusNext] = nextCode
                        nextCode += 1
                    elif resetPolicy == 1:
                        outputCodes.append(dictionary[current])
                        dictionary = {bytes([i]): i for i in range(256)}
                        nextCode = 256
                        current = nextByte
                        continue
                    elif resetPolicy == 2:
                        self.maxDictSize *= 2
                        dictionary[currPlusNext] = nextCode
                        nextCode += 1

                    current = nextByte

            if current:
                outputCodes.append(dictionary[current])

            bitBuffer = bytearray()
            bitPosition = 0

            for code in outputCodes:
                numBits = self.getBitLength(self.maxDictSize - 1)
                bitPosition = self.writeBits(code, numBits, bitBuffer, bitPosition)

            uniqueOutputPath = self.getUniqueFileName("comp", ".bin")
            with open(uniqueOutputPath, "wb") as file:
                file.write(struct.pack("I", self.maxDictSize))
                file.write(struct.pack("B", resetPolicy))
                file.write(struct.pack("H", len(extension)))
                file.write(extension.encode())
                file.write(struct.pack("I", bitPosition))
                file.write(bitBuffer)

            endTime = time.time()
            encodedSize = os.path.getsize(uniqueOutputPath)

            print(f"\nEncoding completed in {endTime - startTime:.2f} seconds")
            print(f"Original size: {originalSize} bytes")
            print(f"Encoded size: {encodedSize} bytes")
            print(f"Compression ratio: {(encodedSize/originalSize)*100:.2f}%")

        except Exception as e:
            print(f"Encoding error: {str(e)}")

    def decodeFile(self, inputPath, _):
        try:
            with open(inputPath, "rb") as file:
                maxDictSize = struct.unpack("I", file.read(4))[0]
                resetPolicy = struct.unpack("B", file.read(1))[0]
                extLength = struct.unpack("H", file.read(2))[0]
                extension = file.read(extLength).decode()
                totalBits = struct.unpack("I", file.read(4))[0]
                bitBuffer = file.read()

            startTime = time.time()

            dictionary = defaultdict(bytes)
            for i in range(256):
                dictionary[i] = bytes([i])
            nextCode = 256

            bitPosition = 0
            outputBuffer = bytearray()
            prevCode = None

            while bitPosition < totalBits:
                numBits = self.getBitLength(maxDictSize - 1)
                if bitPosition + numBits > totalBits:
                    break

                code, bitPosition = self.readBits(numBits, bitBuffer, bitPosition)

                if resetPolicy == 1 and nextCode >= maxDictSize:
                    dictionary.clear()
                    for i in range(256):
                        dictionary[i] = bytes([i])
                    nextCode = 256
                    prevCode = None
                    continue

                if code < 256:
                    entry = bytes([code])
                    outputBuffer.extend(entry)
                    if prevCode is not None and nextCode < maxDictSize:
                        dictionary[nextCode] = dictionary[prevCode] + entry[:1]
                        nextCode += 1
                elif code in dictionary:
                    entry = dictionary[code]
                    outputBuffer.extend(entry)
                    if prevCode is not None and nextCode < maxDictSize:
                        dictionary[nextCode] = dictionary[prevCode] + entry[:1]
                        nextCode += 1
                elif code == nextCode and prevCode is not None:
                    entry = dictionary[prevCode] + dictionary[prevCode][:1]
                    outputBuffer.extend(entry)
                    if nextCode < maxDictSize:
                        dictionary[nextCode] = entry
                        nextCode += 1

                if resetPolicy == 2 and nextCode >= maxDictSize:
                    maxDictSize *= 2

                prevCode = code

            uniqueOutputPath = self.getUniqueFileName("decoded", extension)
            with open(uniqueOutputPath, "wb") as file:
                file.write(outputBuffer)

            endTime = time.time()
            decodedSize = len(outputBuffer)

            print(f"\nDecoding completed in {endTime - startTime:.2f} s")
            print(f"Decoded size: {decodedSize} bytes")

        except Exception as e:
            print(f"Decoding error: {str(e)}")
            raise
