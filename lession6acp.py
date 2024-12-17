import cv2
import numpy as np
import math

# Global variables
points = []  # Stores points for manual measurement
scale_factor = 0.026  # Example: 1 pixel = 0.026 cm (adjust for your image)
output_measurements = []  # Stores all measurements for saving later

# Mouse callback for interactive measurement
def mouse_event(event, x, y, flags, param):
    global points, image_resized
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(image_resized, (x, y), 5, (0, 0, 255), -1)  # Mark point

        if len(points) == 2:
            # Draw a line and calculate distance
            cv2.line(image_resized, points[0], points[1], (0, 255, 0), 2)
            distance_px = math.sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2)
            distance_cm = round(distance_px * scale_factor, 2)
            text = f"{int(distance_px)} px / {distance_cm} cm"
            cv2.putText(image_resized, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            points.clear()  # Reset points for next measurement

            print(f"Measured Distance: {distance_px}px / {distance_cm}cm")

# Function to resize the image for display
def resize_image(img, max_width=800):
    h, w = img.shape[:2]
    if w > max_width:
        scale = max_width / w
        return cv2.resize(img, (int(w * scale), int(h * scale)))
    return img

# Function to draw a grid on the image
def draw_grid(img, grid_size=50):
    h, w = img.shape[:2]
    for x in range(0, w, grid_size):
        cv2.line(img, (x, 0), (x, h), (200, 200, 200), 1)
    for y in range(0, h, grid_size):
        cv2.line(img, (0, y), (w, y), (200, 200, 200), 1)

# Function to detect objects and annotate dimensions
def detect_and_annotate(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 10 and h > 10:  # Filter out small noise
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            w_cm, h_cm = round(w * scale_factor, 2), round(h * scale_factor, 2)
            text = f"W:{w_cm}cm H:{h_cm}cm"
            cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            output_measurements.append(f"Object at ({x}, {y}): Width={w_cm}cm, Height={h_cm}cm")

# Main function
def main():
    global image_resized

    # Load and resize image
    image_path = "3x3 logo.png"  # Replace with your image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Unable to load image.")
        return
    image_resized = resize_image(image)

    # Detect objects and annotate
    detect_and_annotate(image_resized)
    draw_grid(image_resized)

    # Interactive measurement
    print("Click two points to measure distance. Press any key to exit.")
    cv2.imshow("Measurement Tool", image_resized)
    cv2.setMouseCallback("Measurement Tool", mouse_event)
    cv2.waitKey(0)

    # Save results
    output_image_path = "output_annotated_image.jpg"
    cv2.imwrite(output_image_path, image_resized)
    print(f"Annotated image saved to {output_image_path}")

    with open("measurements.txt", "w") as file:
        file.write("\n".join(output_measurements))
    print("Measurements saved to measurements.txt")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
