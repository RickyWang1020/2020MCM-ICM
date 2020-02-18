#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:52:20 2020

@author: lahmwang
"""

from Data import *
import random
import math
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import axes


months = [jan, feb, march, april, may, june, july, aug, sep, oct, nov, dec]
land = [(2,1),(2,2),(3,0),(3,1),(4,13),(4,14),(5,13),(5,14),(6,8),(7,8),(7,9),(8,5),(8,6),(8,9),(8,10),(9,5),(9,6),(9,8),(9,9),(9,10),(9,13),(9,14),(10,10),(10,11),(10,12),(10,13),(10,14),(11,8),(11,9),(11,10),(11,11),(11,12),(11,13),(11,14)]

def start_point():
    return [(6,9),(7,7),(6,7),(5,7),(5,9),(7,10)][random.randint(0,5)]

def valid_direction(pos):
    lati,longi = pos[0],pos[1]
    # it has (theoretically) four possible ways
    result = []
    # to left is ok
    if 0 <= lati <= 11 and longi >= 1 and (lati, longi-1) not in land:
        result.append((lati,longi-1))
    # to right is ok
    if 0 <= lati <= 11 and longi <= 13 and (lati, longi+1) not in land:
        result.append((lati,longi+1))
    # to down is ok
    if 0 <= longi <= 14 and lati <= 10 and (lati+1, longi) not in land:
        result.append((lati+1,longi))
    # to up is ok
    if 0 <= longi <= 14 and lati >= 1 and (lati-1, longi) not in land:
        result.append((lati-1,longi))
    if result:
        return result
    else:
        return False
    
def manh_dis(pos1, pos2):
    y1,x1 = pos1[0],pos1[1]
    y2,x2 = pos2[0],pos2[1]
    distance = abs(y1-y2) + abs(x1-x2)
    return distance

def to_shore(pos, matrix, fish):
    # generate coordinates
    ways = valid_direction(pos)
    # for each possible direction's point, find its smallest distance to a land point
    distances = []
    for point in ways:
        smallest = 100000
        for land_point in land:
            distance = manh_dis(point, land_point)
            if distance < smallest:
                smallest = distance
        distances.append(smallest)
    # go to the way that has the smallest distance to land
    smallest = 100000
    small_points = []
    for index in range(len(distances)):
        if distances[index] < smallest:
            smallest = distances[index]
            small_points = [ways[index]]
        elif distances[index] == smallest:
            small_points.append(ways[index])
    # start weighed random walk (similar to migration)
    if len(small_points) == 1:
        return small_points[0]
    else:
        temps = [float(matrix[i][j]) for (i,j) in small_points]
        if fish == "h":
            fit_temperature = 4.5
        else:
            fit_temperature = 7
        # now calculate the probability
        probability = [0]
        for temp in temps:
            diff = abs(fit_temperature - temp)
            prob = (1/math.log(1 + diff)) / sum([(1/math.log(1 + abs(fit_temperature - i))) for i in temps])
            probability.append(probability[-1] + prob)
        probability[-1] = 1
        dice = random.random()
        for x in range(1, len(probability)):
            if dice <= probability[x]:
                break
        return small_points[x-1]

def spawn(pos):
    return pos

def migration(pos, matrix, fish):
    ways = valid_direction(pos)
    temps = [float(matrix[i][j]) for (i,j) in ways]
    if fish == "h":
        fit_temperature = 4.5
    else:
        fit_temperature = 7
    # now calculate the probability
    probability = [0]
    for temp in temps:
        diff = abs(fit_temperature - temp)
        prob = (1/math.log(1 + diff)) / sum([(1/math.log(1 + abs(fit_temperature - i))) for i in temps])
        probability.append(probability[-1] + prob)
    probability[-1] = 1
    dice = random.random()
    for x in range(1, len(probability)):
        if dice <= probability[x]:
            break
    return ways[x-1]
    

def simulation(fish, result):
    # first, fix the starting point
    current = start_point()
    lati,longi = current[0],current[1]
    
    result[lati][longi] += 1
    
    # each month move a step
    # if it is herring, to-shore(5-7), spawn(8-10), migration(11-4)
    if fish == "h":
        for e in range(624):
            month = e % 12
            year = e // 12
            # get the map for this month
            matrix = months[month][year]
            # if to-shore       
            if e % 12 == 4 or e % 12 == 5 or e % 12 == 6:
                current = to_shore(current, matrix, fish)
                lati,longi = current[0],current[1]
                result[lati][longi] += 1
            # if spawn
            elif e % 12 == 7 or e % 12 == 8 or e % 12 == 9:
                current = spawn(current)
            # if migration
            else:
                current = migration(current, matrix, fish)
                lati,longi = current[0],current[1]
                result[lati][longi] += 1
        return result
    # if it is mackerel, to-shore(2-4), spawn(5-7), migration(8-1)
    else:
        for e in range(624):
            month = e % 12
            year = e // 12
            # get the map for this month
            matrix = months[month][year]
            # if to-shore         
            if e % 12 == 1 or e % 12 == 2 or e % 12 == 3:
                current = to_shore(current, matrix, fish)
                lati,longi = current[0],current[1]
                result[lati][longi] += 1
            # if spawn
            elif e % 12 == 4 or e % 12 == 5 or e % 12 == 6:
                current = spawn(current)
            # if migration
            else:
                current = migration(current, matrix, fish)
                lati,longi = current[0],current[1]
                result[lati][longi] += 1
        return result

def run_herring(times):
    h_result = [ [0 for i in range(15)] for j in range(12)]
    for i in range(times):
        simulation("h", h_result)
    return h_result

def run_mackerel(times):
    m_result = [ [0 for i in range(15)] for j in range(12)]
    for i in range(times):
        simulation("m", m_result)
    return m_result

def draw(mat, fish):
    # define coordinates
    xLabel = [str(m)+"W" for m in range(-20,0,2)]+[0]+[str(n)+"E" for n in range(2,10,2)]
    yLabel = [str(i)+"N" for i in range(70,46,-2)]
    # the canvas
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    # the scale of coordinates
    ax.set_yticks(range(len(yLabel)))
    ax.set_yticklabels(yLabel)
    ax.set_xticks(range(len(xLabel)))
    ax.set_xticklabels(xLabel)
    # color filling
    im = ax.imshow(mat, cmap=plt.cm.hot_r)
    # color bar
    plt.colorbar(im)
    # title
    plt.title("Scotland Herring's Migration Paths") if fish == "h" else plt.title("Scotland Mackerel's Migration Paths")
    plt.show()
    print(mat)
  
   
    
h_data = run_herring(500)
d = draw(h_data, "h")

m_data = run_mackerel(500)
d = draw(m_data, "m")
