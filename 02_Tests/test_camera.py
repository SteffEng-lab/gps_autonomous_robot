import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open the camera")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imwrite("test_frame.jpg", frame)
    print("Frame saved to test_frame.jpg")
else:
    print("Error: Could not read frame")

cap.release()
