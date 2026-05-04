import numpy as np

class DynamicTimeWrapping:
    def __init__(self):
        self.movement1 = None
        self.movement2 = None
        self.dtw = None

    def register_movements(self, movement1, movement2):
        self.movement1 = movement1
        self.movement2 = movement2

    def compare(self):
        if self.movement1 is None or self.movement2 is None:
            return
        seq1 = self.movement1.key_frames
        seq2 = self.movement2.key_frames

        n = len(seq1)
        m = len(seq2)

        self.dtw = np.full((n, m), np.inf)
        self.dtw[0, 0] = 0
        for i in range(1, n+1):
            for j in range(1, m+1):
                cost = self.get_distance(seq1[i-1], seq2[i-1])
                self.dtw[i, j] = cost + min(self.dtw[i-1, j],
                                            self.dtw[i, j-1],
                                            self.dtw[i-1, j-1])
        return self.dtw[n, m]
    @staticmethod
    def get_distance(frame1, frame2):
        return np.linalg.norm(frame1 - frame2)
