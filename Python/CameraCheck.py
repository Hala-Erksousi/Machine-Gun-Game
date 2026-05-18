import cv2


def scan_cameras(max_index=5):
    print("Scanning cameras with cv2.CAP_DSHOW...")
    for index in range(max_index + 1):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        opened = cap.isOpened()
        read_ok = False
        shape = None

        if opened:
            read_ok, frame = cap.read()
            if read_ok and frame is not None:
                shape = frame.shape

        print(f"Camera {index}: opened={opened}, read={read_ok}, shape={shape}")
        cap.release()


if __name__ == "__main__":
    scan_cameras()
