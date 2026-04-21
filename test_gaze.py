import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

def get_head_pose_v2(face_landmarks, img_w, img_h):
    face_2d = []
    indices = [1, 152, 33, 263, 61, 291]
    model_3d = np.array([
        [0.0, 0.0, 0.0],
        [0.0, -330.0, -65.0],
        [-225.0, 170.0, -135.0],
        [225.0, 170.0, -135.0],
        [-150.0, -150.0, -125.0],
        [150.0, -150.0, -125.0]
    ], dtype=np.float64)
    for idx in indices:
        lm = face_landmarks.landmark[idx]
        face_2d.append([lm.x * img_w, lm.y * img_h])
    face_2d = np.array(face_2d, dtype=np.float64)
    cam_matrix = np.array([[img_w, 0, img_w / 2], [0, img_w, img_h / 2], [0, 0, 1]])
    success, rot_vec, trans_vec = cv2.solvePnP(model_3d, face_2d, cam_matrix, np.zeros((4, 1)))
    rmat, _ = cv2.Rodrigues(rot_vec)
    pitch = np.arcsin(-rmat[2, 0])
    yaw = np.arctan2(rmat[2, 1], rmat[2, 2])
    return np.degrees(pitch), np.degrees(yaw)

def get_gaze_ratio(face_landmarks, eye_indices, iris_indices):
    lm = face_landmarks.landmark
    x_left = lm[eye_indices[0]].x
    x_right = lm[eye_indices[8]].x
    x_iris = np.mean([lm[i].x for i in iris_indices])
    width = abs(x_right - x_left)
    if width == 0: return 0.5
    return (x_iris - min(x_left, x_right)) / width

def analyze_video(path):
    cap = cv2.VideoCapture(path)
    with mp_face_mesh.FaceMesh(refine_landmarks=True) as fm:
        frames = 0
        yaws = []
        gazes = []
        while cap.isOpened() and frames < 100:
            ret, frame = cap.read()
            if not ret: break
            h, w, _ = frame.shape
            res = fm.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if res.multi_face_landmarks:
                lms = res.multi_face_landmarks[0]
                pitch, raw_yaw = get_head_pose_v2(lms, w, h)
                yaw_c = raw_yaw - 180 if raw_yaw > 0 else raw_yaw + 180
                
                ratio_l = get_gaze_ratio(lms, LEFT_EYE, LEFT_IRIS)
                ratio_r = get_gaze_ratio(lms, RIGHT_EYE, RIGHT_IRIS)
                avg_gaze = (ratio_l + ratio_r) / 2
                
                yaws.append(yaw_c)
                gazes.append(avg_gaze)
            frames += 1
        print(f"{path}: avg_yaw={np.mean(yaws):.1f}, avg_gaze={np.mean(gazes):.3f}")

analyze_video("video_metrics/gaze/media/custom_faceright_contact.mp4")
analyze_video("video_metrics/gaze/media/custom_faceright_nocontact.mp4")
