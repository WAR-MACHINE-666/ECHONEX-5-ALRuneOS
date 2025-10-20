def _render_anime(self, frame, emotional_state, blendshapes):
        """Render anime style avatar"""
        # Anime style with more simplified features
        # For brevity, using a modified version of the stylized renderer
        
        # Get primary emotion and intensity
        primary_emotion = emotional_state["primary_emotion"]
        intensity = emotional_state["emotional_intensity"]
        
        # Create a colored background based on emotional state
        color = self._emotion_to_color(primary_emotion, intensity)
        frame = np.ones((self.resolution[1], self.resolution[0], 3), dtype=np.uint8) * color
        
        # Draw a simple face - oval for anime
        center_x = self.resolution[0] // 2
        center_y = self.resolution[1] // 2
        radius_x = min(center_x, center_y) // 2
        radius_y = radius_x * 1.2  # Oval face
        
        # Draw face
        cv2.ellipse(frame, (center_x, center_y), (radius_x, radius_y), 
                   0, 0, 360, (255, 240, 220), -1)
        
        # Draw eyes - much larger for anime
        eye_size_x = radius_x // 2.5
        eye_size_y = radius_y // 4
        left_eye_x = center_x - radius_x // 2
        right_eye_x = center_x + radius_x // 2
        eye_y = center_y - radius_y // 6
        
        # Adjust eye openness based on blendshapes
        eye_openness = 1.0 - blendshapes.get("eye_closed", 0)
        eye_height = int(eye_size_y * eye_openness)
        
        # Anime eyes
        cv2.ellipse(frame, (left_eye_x, eye_y), (eye_size_x, eye_height), 
                   0, 0, 360, (10, 10, 10), -1)
        cv2.ellipse(frame, (right_eye_x, eye_y), (eye_size_x, eye_height), 
                   0, 0, 360, (10, 10, 10), -1)
        
        # Add eye highlights - larger for anime
        highlight_size = eye_size_x // 2
        cv2.circle(frame, (left_eye_x + highlight_size//2, eye_y - highlight_size//4), 
                  highlight_size, (255, 255, 255), -1)
        cv2.circle(frame, (right_eye_x + highlight_size//2, eye_y - highlight_size//4), 
                  highlight_size, (255, 255, 255), -1)
        
        # Anime often skips eyebrows for neutral expressions
        if blendshapes.get("eyebrow_raise", 0) > 0.3 or blendshapes.get("eyebrow_furrow", 0) > 0.3:
            # Draw eyebrows - thin lines for anime
            eyebrow_width = eye_size_x * 1.5
            eyebrow_height = eye_size_y // 4
            
            # Adjust eyebrow position based on blendshapes
            eyebrow_raise = blendshapes.get("eyebrow_raise", 0)
            eyebrow_furrow = blendshapes.get("eyebrow_furrow", 0)
            
            left_eyebrow_y = eye_y - eye_size_y - int(eyebrow_raise * 30)
            right_eyebrow_y = left_eyebrow_y
            
            # Angle for eyebrows
            left_angle = -eyebrow_furrow * 40
            right_angle = eyebrow_furrow * 40
            
            cv2.ellipse(frame, (left_eye_x, left_eyebrow_y), (eyebrow_width, eyebrow_height), 
                       left_angle, 0, 180, (10, 10, 10), -1)
            cv2.ellipse(frame, (right_eye_x, right_eyebrow_y), (eyebrow_width, eyebrow_height), 
                       right_angle, 0, 180, (10, 10, 10), -1)
        
        # Draw mouth - small for anime
        mouth_width = radius_x // 2
        
        # Adjust mouth based on blendshapes
        mouth_open = blendshapes.get("mouth_open", 0)
        smile = blendshapes.get("smile", 0)
        frown = blendshapes.get("frown", 0)
        
        # Anime often uses simple lines for mouth
        mouth_height = int(radius_y * 0.05 + mouth_open * radius_y * 0.3)
        mouth_y = center_y + radius_y // 3
        
        # Adjust mouth curve based on smile/frown
        mouth_curve = smile - frown
        
        # Draw mouth - simple for anime
        if mouth_open < 0.2:  # Closed mouth
            # Just a line
            cv2.line(frame, 
                    (center_x - int(mouth_width//2 * (1 + mouth_curve)), 
                     mouth_y + int(mouth_curve * 20)),
                    (center_x + int(mouth_width//2 * (1 + mouth_curve)), 
                     mouth_y - int(mouth_curve * 20)),
                    (10, 10, 10), 2)
        else:  # Open mouth
            # Small oval
            cv2.ellipse(frame, (center_x, mouth_y), 
                       (int(mouth_width * (1 + mouth_curve * 0.5)), mouth_height), 
                       0, 0, 360, (10, 10, 10), -1)
        
        return frame
    
    def _render_default(self, frame, emotional_state, blendshapes):
        """Default rendering when style is not recognized"""
        # Simple rendering with basic shapes
        return self._render_stylized(frame, emotional_state, blendshapes)
    
    def _emotion_to_color(self, emotion, intensity):
        """Convert emotion to background color"""
        # Base colors for emotions
        emotion_colors = {
            "happiness": (50, 150, 255),  # Yellow
            "sadness": (150, 50, 0),      # Blue
            "anger": (0, 0, 150),         # Red
            "fear": (100, 0, 100),        # Purple
            "surprise": (0, 100, 255),    # Orange
            "disgust": (0, 100, 0),       # Green
            "contempt": (50, 0, 50),      # Brown
            "neutral": (50, 50, 50)       # Gray
        }
        
        # Get base color
        base_color = emotion_colors.get(emotion, (50, 50, 50))
        
        # Adjust intensity (higher intensity = more saturated)
        color = tuple(int(c * intensity) for c in base_color)
        
        return color
    
    def get_current_frame(self):
        """Get the current rendered frame"""
        return self.current_frame
    
    def set_style(self, style):
        """Change avatar style"""
        self.style = style
        self.load_assets()


class BlendshapeMapper:
    """Maps emotional states to avatar blendshapes"""
    
    def __init__(self):
        """Initialize blendshape mapper"""
        # Define mappings from emotions to blendshapes
        self.emotion_to_blendshape_map = {
            "happiness": {
                "smile": 1.0,
                "eyebrow_raise": 0.3,
                "eye_closed": 0.3  # Slight eye narrowing for genuine smile
            },
            "sadness": {
                "frown": 0.7,
                "eyebrow_raise": 0.3,
                "eyebrow_furrow": 0.3,
                "mouth_open": 0.1
            },
            "anger": {
                "eyebrow_furrow": 0.8,
                "eye_closed": 0.2,
                "frown": 0.5
            },
            "fear": {
                "eyebrow_raise": 0.8,
                "eye_closed": 0.0,  # Wide eyes
                "mouth_open": 0.3
            },
            "surprise": {
                "eyebrow_raise": 1.0,
                "eye_closed": 0.0,  # Wide eyes
                "mouth_open": 0.7
            },
            "disgust": {
                "eyebrow_furrow": 0.5,
                "frown": 0.3,
                "eye_closed": 0.3
            },
            "contempt": {
                "eyebrow_raise": 0.3,
                "smile": 0.3,  # Asymmetric smile for contempt
                "eye_closed": 0.3
            },
            "neutral": {
                "smile": 0.0,
                "frown": 0.0,
                "eyebrow_raise": 0.0,
                "eyebrow_furrow": 0.0,
                "eye_closed": 0.0,
                "mouth_open": 0.0
            }
        }
    
    def map_emotions_to_blendshapes(self, emotional_state):
        """
        Map emotional state to blendshape values
        
        Args:
            emotional_state: Current emotional state
            
        Returns:
            Dictionary of blendshape values
        """
        # Initialize blendshapes with zeros
        blendshapes = {
            "smile": 0.0,
            "frown": 0.0,
            "eyebrow_raise": 0.0,
            "eyebrow_furrow": 0.0,
            "eye_closed": 0.0,
            "mouth_open": 0.0
        }
        
        # Get emotion values
        emotion_values = emotional_state["emotion_values"]
        
        # Apply each emotion's contribution to blendshapes
        for emotion, value in emotion_values.items():
            if emotion in self.emotion_to_blendshape_map:
                for blendshape, intensity in self.emotion_to_blendshape_map[emotion].items():
                    blendshapes[blendshape] += value * intensity
        
        # Ensure values are in range 0-1
        for blendshape in blendshapes:
            blendshapes[blendshape] = min(1.0, max(0.0, blendshapes[blendshape]))
        
        # Apply intensity modifier
        intensity = emotional_state["emotional_intensity"]
        for blendshape in blendshapes:
            if blendshape != "eye_closed":  # Don't reduce eye_closed with intensity
                blendshapes[blendshape] *= intensity
        
        return blendshapes


class FPSCounter:
    """Simple FPS counter"""
    
    def __init__(self, avg_frames=30):
        """Initialize FPS counter"""
        self.frame_times = deque(maxlen=avg_frames)
        self.last_time = time.time()
    
    def update(self):
        """Update FPS counter"""
        current_time = time.time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time
    
    def get_fps(self):
        """Get current FPS"""
        if not self.frame_times:
            return 0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time == 0:
            return 0
            
        return 1.0 / avg_frame_time


# Example usage
def main():
    # Initialize the avatar system
    avatar = SPECTRAEmotionalAvatar(avatar_style="anime", render_resolution=(640, 480))
    
    # Start preview window
    avatar.start_preview()
    
    # Enable debug mode to see emotion values
    avatar.toggle_debug_mode()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            # Capture frame from webcam
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame for processing
            frame = cv2.resize(frame, (640, 480))
            
            # Process frame to update avatar
            avatar.process_frame(frame)
            
            # Display original frame
            cv2.imshow('Webcam', frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        avatar.close()


if __name__ == "__main__":
    main()