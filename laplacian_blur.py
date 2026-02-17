import cv2

def determine_blur_laplacian(LR, path):
    gray_image = cv2.cvtColor(LR, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray_image,  cv2.CV_64F)
    var_laplacian = laplacian.var()

    if var_laplacian < 100:
        return True
    else:
        return False