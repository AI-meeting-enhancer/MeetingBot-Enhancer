#include "ZoomSDKRendererDelegate.h"

// Constructor for the ZoomSDKRendererDelegate class
ZoomSDKRendererDelegate::ZoomSDKRendererDelegate() {
    // Initialize X11 threading support for graphics rendering
    XInitThreads();

    // Load the Haar Cascade classifier for face detection
    if (!m_cascade.load("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"))
        Log::error("failed to load cascade file"); // Log error if loading fails

    m_faces.reserve(2); // Reserve space for detected faces
    m_socketServer.start(); // Start the socket server for communication
}

// Callback method that is triggered when a raw data frame is received
void ZoomSDKRendererDelegate::onRawDataFrameReceived(YUVRawDataI420 *data) {
    Log::info("Here is on received streawming...");
    // Launch an asynchronous task to process the received raw data
    auto res = async(launch::async, [&] {
        // Create an OpenCV Mat object for the I420 format
        Mat I420(data->GetStreamHeight() * 3 / 2, data->GetStreamWidth(), CV_8UC1, data->GetBuffer());
        Mat small, gray; // Mat objects for resized and grayscale images

        // Convert the I420 format to grayscale
        cvtColor(I420, gray, COLOR_YUV2GRAY_I420);

        // Resize the grayscale image for face detection
        resize(gray, small, Size(), m_fx, m_fx, INTER_LINEAR);
        equalizeHist(small, small); // Enhance contrast of the resized image

        // Detect faces in the processed image
        m_cascade.detectMultiScale(small, m_faces, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));

        // Log the number of faces detected
        stringstream ss;
        ss << m_faces.size();
        m_socketServer.writeStr(ss.str()); // Send the number of faces to the socket server

        // Draw rectangles around detected faces every other frame
        if (m_frameCount++ % 2 == 0) {
            Scalar color = Scalar(0, 0, 255); // Set rectangle color to red
            for (size_t i = 0; i < m_faces.size(); i++) {
                Rect r = m_faces[i]; // Get the rectangle for the detected face
                // Draw the rectangle on the grayscale image
                rectangle(gray, Point(cvRound(r.x * m_scale), cvRound(r.y * m_scale)),
                          Point(cvRound((r.x + r.width - 1) * m_scale),
                                cvRound((r.y + r.height - 1) * m_scale)), color, 3, 8, 0);
            }

            // Display the processed image in a window
            imshow(c_window, gray);
        }
    });
}

// Method to write raw YUV data to a file
void ZoomSDKRendererDelegate::writeToFile(const string &path, YUVRawDataI420 *data) {
    // Open the specified file in binary append mode
    std::ofstream file(path, std::ios::out | std::ios::binary | std::ios::app);
    if (!file.is_open())
        return Log::error("failed to open video output file: " + path); // Log error if file cannot be opened

    // Write the raw data buffer to the file
    file.write(data->GetBuffer(), data->GetBufferLen());
    
    file.close(); // Close the file
    file.flush(); // Flush the file stream
}

// Method to set the directory for output files
void ZoomSDKRendererDelegate::setDir(const string &dir) {
    m_dir = dir; // Store the directory path
}

// Method to set the filename for output files
void ZoomSDKRendererDelegate::setFilename(const string &filename) {
    m_filename = filename; // Store the filename
}