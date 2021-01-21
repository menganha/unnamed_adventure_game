"""
Utility functions which don't belong to other particular classes
"""
import pygame


def scale_rect(rectangle: pygame.Rect, scale=2):
    rectangle.x = rectangle.x*scale
    rectangle.y = rectangle.y*scale
    rectangle.w = rectangle.w*scale
    rectangle.h = rectangle.h*scale
    return rectangle
