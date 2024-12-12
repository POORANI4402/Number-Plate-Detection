# Number Plate Detection System

This project implements a **Number Plate Detection System** using **OpenCV** for real-time video capture and **EasyOCR** for optical character recognition (OCR). The system captures live video feed from a webcam, detects vehicle number plates, and extracts the text from them. If the detected text matches an expected plate, an email notification is sent.

## Features:
- **Live Video Feed**: Displays real-time video captured from a webcam.
- **Number Plate Detection**: Uses Haar Cascade Classifier for detecting number plates in the video feed.
- **OCR Text Extraction**: Uses **EasyOCR** to extract text from the detected number plate.
- **Match Checking**: Compares the extracted number plate text against a list of expected plates.
- **Email Notification**: Sends an email with the detected text and the match status.

## Technologies Used:
- **Python**
- **Flask**: Web framework to run the application
- **OpenCV**: For image processing and number plate detection
- **EasyOCR**: For Optical Character Recognition (OCR) to extract text from the detected plates
- **SMTP**: To send email notifications


## How It Works:

1. **Video Feed**: 
   - When the application runs, it starts capturing the webcam video and displays it on the webpage.

2. **Plate Detection**: 
   - The application detects potential number plates in the live feed using a pre-trained **Haar Cascade Classifier** model.

3. **Text Extraction**: 
   - If a number plate is detected, the system captures the plate region and processes it using **EasyOCR** to extract the text.

4. **Match Checking**: 
   - The extracted text is compared with the list of expected plates found in the `check.txt` file.

5. **Email Notification**: 
   - An email is sent to the specified receiver with the detected number plate text and whether it matched the expected plates.

## IMAGES 

![image](https://github.com/user-attachments/assets/05f3e291-b368-4382-848c-ed202ea5ee28)


![Screenshot (373)](https://github.com/user-attachments/assets/1ccfea1d-cd99-4a5c-bd0f-dfca2298c9de)

![image](https://github.com/user-attachments/assets/a8a82dfd-8f9c-4651-aa3c-d9cc1b5f6320)


## Prerequisites:
Ensure you have **Python 3.x** installed on your machine. Install the required libraries by running:

```bash
pip install flask opencv-python easyocr


