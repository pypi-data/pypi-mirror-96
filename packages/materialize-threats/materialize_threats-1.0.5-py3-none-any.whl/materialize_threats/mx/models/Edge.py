from ..utils import MxConst
from .GraphObj import GraphObj


class Edge(GraphObj):
    def __init__(self, sid, gid, value, fr, to, curve):
       
        super(Edge, self).__init__(sid, gid, value)

        self.fr = fr
        self.to = to
        self.curve = curve
        self.style = None
        self.dir = None
        self.arrowtail = None

    def curve_start_end(self):
        if self.dir == MxConst.BACK:
            return self.curve.end, self.curve.start
        else:
            return self.curve.start, self.curve.end
