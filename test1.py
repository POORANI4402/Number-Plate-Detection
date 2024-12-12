from flask import Flask, render_template, Response, redirect, url_for, send_from_directory
import cv2
import easyocr
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

# Set paths
app.config['UPLOAD_FOLDER'] = "plates"  # Directory to save captured images
harcascade_path = "model/haarcascade_russian_plate_number.xml"

# Ensure the "plates" directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load expected text from check.txt
with open("check.txt", "r") as file:
    expected_texts = [line.strip() for line in file]

# EasyOCR reader initialization
reader = easyocr.Reader(['en'])

# Email configuration
EMAIL_ADDRESS = "s62854973@gmail.com"  # Replace with your sender email
EMAIL_PASSWORD = "kkts pozm epne kjwi"          # Replace with your sender email password
RECEIVER_EMAIL = "receiver659@gmail.com"  # Replace with the receiver's email

# Initialize video capture
camera = cv2.VideoCapture(0)

@app.route('/')
def home():
    return render_template('index.html')

# Route to provide live video feed
@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to capture the current frame
@app.route('/capture')
def capture():
    # Capture the current frame from the webcam
    success, frame = camera.read()

    if not success:
        return "Failed to capture image from webcam", 500

    # Save the captured frame
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"captured_{timestamp}.jpg"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    cv2.imwrite(file_path, frame)

    # Process the image for number plate detection
    extracted_text, processed_image_path = detect_number_plate(file_path)

    # Check if the text matches expected plates
    match_status = "Match Found!" if extracted_text in expected_texts else "No Match Found!"

    # Send email notification
    send_email_notification(match_status, extracted_text)

    # Redirect to the result page
    return render_template(
        'result.html',
        uploaded_image_url=file_name,
        processed_image_url=processed_image_path,
        extracted_text=extracted_text,
        match_status=match_status
    )

# Function to process the image and detect number plates
def detect_number_plate(image_path):
    # Load the Haar Cascade model
    plate_cascade = cv2.CascadeClassifier(harcascade_path)

    # Read the uploaded image
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect number plates
    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
    img_roi = None

    for (x, y, w, h) in plates:
        area = w * h
        if area > 500:
            img_roi = img[y:y + h, x:x + w]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            break

    # Save the processed image with annotations
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "processed_" + os.path.basename(image_path))
    cv2.imwrite(processed_image_path, img)

    if img_roi is not None:
        # Preprocess the ROI for better OCR
        gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Use OCR to extract text
        extracted_text = reader.readtext(thresholded, detail=0, paragraph=False)
        extracted_text = " ".join(extracted_text).strip()

        # Clean up the extracted text
        extracted_text_cleaned = re.sub(r'[^a-zA-Z0-9]', '', extracted_text)
        return extracted_text_cleaned, "processed_" + os.path.basename(image_path)

    return "No plate detected", "processed_" + os.path.basename(image_path)

# Function to send email notification
def send_email_notification(match_status, extracted_text):
    subject = "Number Plate Detection Result"
    body = f"The detected text is: {extracted_text}\n\nStatus: {match_status}"

    # Email message setup
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use your email provider's SMTP server
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Serve uploaded and processed images
@app.route('/plates/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
