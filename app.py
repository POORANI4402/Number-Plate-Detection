from flask import Flask, render_template, Response, redirect, url_for, send_from_directory
import cv2
import easyocr
import os
import re
from datetime import datetime

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "plates"
harcascade_path = "model/haarcascade_russian_plate_number.xml"

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

with open("check.txt", "r") as file:
    expected_texts = [line.strip() for line in file]

reader = easyocr.Reader(['en'])
camera = cv2.VideoCapture(0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        plate_cascade = cv2.CascadeClassifier(harcascade_path)
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                # Real-time number plate detection
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                plates = plate_cascade.detectMultiScale(gray_frame, 1.1, 4)
                for (x, y, w, h) in plates:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, "Number Plate", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                # Encode frame
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')


@app.route('/capture')
def capture():
    success, frame = camera.read()
    if not success:
        return "Failed to capture image from webcam", 500

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"captured_{timestamp}.jpg"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    cv2.imwrite(file_path, frame)

    extracted_text, processed_image_path = detect_number_plate(file_path)

    match_status = "Match Found!" if extracted_text in expected_texts else "No Match Found!"

    # Release the camera after capturing
    camera.release()

    return render_template(
        'result.html',
        uploaded_image_url=file_name,
        processed_image_url=processed_image_path,
        extracted_text=extracted_text,
        match_status=match_status
    )

def detect_number_plate(image_path):
    plate_cascade = cv2.CascadeClassifier(harcascade_path)
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
    img_roi = None

    for (x, y, w, h) in plates:
        area = w * h
        if area > 500:
            img_roi = img[y:y + h, x:x + w]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            break

    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "processed_" + os.path.basename(image_path))
    cv2.imwrite(processed_image_path, img)

    if img_roi is not None:
        gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        extracted_text = reader.readtext(thresholded, detail=0, paragraph=False)
        extracted_text = " ".join(extracted_text).strip()

        extracted_text_cleaned = re.sub(r'[^a-zA-Z0-9]', '', extracted_text)
        return extracted_text_cleaned, "processed_" + os.path.basename(image_path)

    return "No plate detected", "processed_" + os.path.basename(image_path)

@app.route('/plates/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)




# def capture():
#     success, frame = camera.read()
#     if not success:
#         return "Failed to capture image from webcam", 500

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     file_name = f"captured_{timestamp}.jpg"
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
#     cv2.imwrite(file_path, frame)

#     extracted_text, processed_image_path = detect_number_plate(file_path)

#     match_status = "Match Found!" if extracted_text in expected_texts else "No Match Found!"

#     return render_template(
#         'result.html',
#         uploaded_image_url=file_name,
#         processed_image_url=processed_image_path,
#         extracted_text=extracted_text,
#         match_status=match_status
#     )