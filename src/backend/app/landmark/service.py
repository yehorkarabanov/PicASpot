from app.landmark.repository import LandmarkRepository


class LandmarkService:
    def __init__(self, landmark_repository: LandmarkRepository):
        self.landmark_repository = landmark_repository
