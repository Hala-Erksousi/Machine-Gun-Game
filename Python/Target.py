import math
class Target:
    def __init__(self, target_id, initial_bbox):
        self.id = target_id
        self.initial_x, self.initial_y, self.initial_w, self.initial_h = initial_bbox
        self.current_x, self.current_y, self.current_w, self.current_h = initial_bbox
        self.is_standing = True
        self.fallen_frame_count = 0 
        self.was_counted_as_fallen = False
        self.standing_center_y = self.initial_y + self.initial_h // 2
        self.fall_threshold_y = self.initial_h * 0.2

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)