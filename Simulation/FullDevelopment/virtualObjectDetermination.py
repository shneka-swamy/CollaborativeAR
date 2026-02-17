import numpy as np
import scipy

# Convert the quartenion coordinate value to rotation value
def convert_rotations(quaternions):
    return scipy.spatial.transform.Rotation.from_quat(quaternions).as_matrix()

# Converts 3D pose estimation to the image coordinate
def threeDToTwoD(pose, pose_object, fx, fy, cx, cy, distort):
    pose_rotation = convert_rotations(np.array(pose[4:8]))
    pose_translation = np.array(pose[1:4])

    Pc = np.matmul(pose_rotation, pose_object) + pose_translation
    euclidean = np.linalg.norm([pose_translation - pose_object]).item()

    x2_plus_y2 = Pc[0]**2 + Pc[1]**2
    theta = np.arctan2(np.sqrt(x2_plus_y2), Pc[2])
    psi = np.arctan2(Pc[1], Pc[0])

    theta2 = theta**2
    theta3 = theta2*theta
    theta5 = theta3*theta2
    theta7 = theta5*theta2
    theta9 = theta7*theta2

    d_theta = theta + distort[0] * theta3 + distort[1] * theta5 + distort[2] * theta7 + distort[3] * theta9
    
    x_img = fx * d_theta * np.cos(psi) + cx
    y_img = fy * d_theta * np.sin(psi) + cy

    return x_img, y_img, euclidean

# Check if the image point falls in the visibility window of the virtual object
def isVisible(x_img, y_img):
    if x_img >= 0 and x_img < 680 and y_img >= 0 and y_img < 320:
        return True
    else:
        return False

# Determine the virtual objects that are visible
def determineVisibilityAll(poses, pose_object, fx, fy, cx, cy, distort):
    visibility = []
    distance = []
    for pose in poses:
        x_img, y_img, euclidean = threeDToTwoD(pose, pose_object, fx, fy, cx, cy, distort)
        if isVisible(x_img, y_img):
            visibility.append(1)
        else:
            visibility.append(0)
        distance.append(euclidean)
    return visibility, distance


