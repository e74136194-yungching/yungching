import numpy as np

class Body:
    def __init__(self, mass, position, velocity):
        self.mass = mass
        self.r = position.astype(float)
        self.v = velocity.astype(float)
        self.trail = []

class ThreeBodySystem:
    def __init__(self, bodies, G):
        self.bodies = bodies
        self.G = G

    def compute_accelerations(self):
        accelerations = []
        for i, bi in enumerate(self.bodies):
            a = np.zeros(2)
            for j, bj in enumerate(self.bodies):
                if i != j:
                    diff = bj.r - bi.r
                    dist = np.linalg.norm(diff) + 1e-5
                    a += self.G * bj.mass * diff / dist**3
            accelerations.append(a)
        return accelerations

    def step(self, dt):
        accs = self.compute_accelerations()
        for body, a in zip(self.bodies, accs):
            body.v += a * dt
            body.r += body.v * dt
            body.trail.append(body.r.copy())

    def total_energy(self):
        kinetic = 0
        potential = 0

        for body in self.bodies:
            kinetic += 0.5 * body.mass * np.linalg.norm(body.v)**2

        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                ri = self.bodies[i].r
                rj = self.bodies[j].r
                dist = np.linalg.norm(ri - rj)
                potential -= self.G * self.bodies[i].mass * self.bodies[j].mass / dist

        return kinetic + potential
