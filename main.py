import pygame
import random
import numpy as np
import math

WIDTH, HEIGHT = 800, 600
BOID_COUNT = 50
MAX_SPEED = 5
PERCEPTION = 75
MAX_FORCE = 0.3
WIDTH, HEIGHT = 800, 600
BOID_SIZE = 5
VIEW_ANGLE = 90 * (math.pi * 180)
BOID_COUNT = 50


class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        vec = (np.random.rand(2) - 0.5) * 10
        self.velocity = pygame.Vector2(vec[0], vec[1])

        vec = (np.random.rand(2) - 0.5) / 2
        self.acceleration = pygame.Vector2(vec[0], vec[1])

    def draw(self, window):
        angle = math.atan2(self.velocity.y, self.velocity.x)

        point1 = (
            self.position.x + BOID_SIZE * math.cos(angle),
            self.position.y + BOID_SIZE * math.sin(angle),
        )
        point2 = (
            self.position.x + BOID_SIZE * math.cos(angle + 2.5),
            self.position.y + BOID_SIZE * math.sin(angle + 2.5),
        )
        point3 = (
            self.position.x + BOID_SIZE * math.cos(angle - 2.5),
            self.position.y + BOID_SIZE * math.sin(angle - 2.5),
        )

        pygame.draw.polygon(window, (255, 255, 255), [point1, point2, point3])

    def update(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)

        self.acceleration += alignment
        self.acceleration += cohesion
        self.acceleration += separation

        self.position += self.velocity
        self.velocity += self.acceleration

        if np.linalg.norm(self.velocity) > MAX_SPEED:
            self.velocity = self.velocity / np.linalg.norm(self.velocity) * MAX_SPEED

        self.acceleration = pygame.Vector2(0, 0)

        # check the screen edge collisions and wrap if needed
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH

        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def align(self, boids):
        steering = pygame.Vector2()
        total = 0
        avg_vec = pygame.Vector2()
        for boid in boids:
            distance = np.linalg.norm(boid.position - self.position)
            if distance < PERCEPTION:
                diff = boid.position - self.position
                angle = self.velocity.angle_to(diff)

                if -VIEW_ANGLE <= angle <= VIEW_ANGLE:
                    avg_vec += boid.velocity
                    total += 1
        if total > 0:
            avg_vec /= total
            avg_vec = (avg_vec / np.linalg.norm(avg_vec)) * MAX_SPEED
            steering = avg_vec - self.velocity
        return steering

    def cohesion(self, boids):
        steering = pygame.Vector2()
        total = 0
        centre_of_mass = pygame.Vector2()
        for boid in boids:
            distance = np.linalg.norm(boid.position - self.position)
            if distance < PERCEPTION:
                diff = boid.position - self.position
                angle = self.velocity.angle_to(diff)
                if -VIEW_ANGLE <= angle <= VIEW_ANGLE:
                    centre_of_mass += boid.position
                    total += 1
        if total > 0:
            centre_of_mass /= total
            vec_to_com = centre_of_mass - self.position
            if np.linalg.norm(vec_to_com) > 0:
                vec_to_com = (vec_to_com / np.linalg.norm(vec_to_com)) * MAX_SPEED
            steering = vec_to_com - self.velocity
            if np.linalg.norm(steering) > MAX_FORCE:
                steering = (steering / np.linalg.norm(steering)) * MAX_FORCE
        return steering

    def separation(self, boids):
        steering = pygame.Vector2()
        total = 0
        avg_vec = pygame.Vector2()
        for boid in boids:
            distance = np.linalg.norm(boid.position - self.position)
            if self.position != boid.position and 0 < distance < PERCEPTION / 2:
                diff = self.position - boid.position
                angle = self.velocity.angle_to(diff)
                if -VIEW_ANGLE <= angle <= VIEW_ANGLE:
                    diff /= distance
                    avg_vec += diff
                    total += 1
        if total > 0:
            avg_vec /= total
            if np.linalg.norm(avg_vec) > 0:
                avg_vec = (avg_vec / np.linalg.norm(avg_vec)) * MAX_SPEED
            steering = avg_vec - self.velocity
            if np.linalg.norm(steering) > MAX_FORCE:
                steering = (steering / np.linalg.norm(steering)) * MAX_FORCE
        return steering

    def apply_behaviour(self, boids):
        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)

        self.acceleration += alignment
        self.acceleration += cohesion
        self.acceleration += separation


pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Boids")

boids = [
    Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(BOID_COUNT)
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.fill((0, 0, 0))

    for boid in boids:
        boid.draw(window)
        boid.update(boids)

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
