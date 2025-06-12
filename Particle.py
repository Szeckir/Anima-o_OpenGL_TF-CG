from Ponto import Ponto
import random

class Particle:
    def __init__(self, initial_pos: Ponto):
        self.original_pos = initial_pos.copy() 
        self.current_pos = initial_pos.copy()  
        self.velocity = Ponto(0, 0, 0)         
        self.acceleration = Ponto(0, 0, 0)     
        self.color = [random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0)] ## rgb aleatório

    def update(self, dt: float):
        # delta tempo
        self.velocity = self.velocity + (self.acceleration * dt)
        self.current_pos = self.current_pos + (self.velocity * dt)
        self.acceleration = Ponto(0, 0, 0) 

    def apply_force(self, force: Ponto):
        self.acceleration = self.acceleration + force

    def reset_position(self):
        self.current_pos = self.original_pos.copy()
        self.velocity = Ponto(0, 0, 0)
        self.acceleration = Ponto(0, 0, 0)