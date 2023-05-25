import serial
import time
from graphics import *
import math

import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
from networkx import make_max_clique_graph
from networkx.algorithms.approximation import clique
from collections import defaultdict
from pyqubo import Binary
import random

import requests
import json
import boto3

import warnings
warnings.filterwarnings("ignore")

from qubovert.problems import SetCover
import qubovert

from qubovert.problems import SetCover
from qubovert.utils import qubo_to_matrix





# Changes waiter connections so it fits library
def create_v(V1, tables_to_serve):
  V=[]
  tables_requiring_service= list(tables_to_serve)
  for i in V1:
    waiters_tables=set({})
    
    for j in i:
      if j in tables_requiring_service:
        waiters_tables.add(j)
      
    V.append(waiters_tables)
  
  return V


def login(username, password, user_id):
    client = boto3.client("cognito-idp", region_name="eu-west-1")
    response = client.initiate_auth(ClientId=user_id, AuthFlow="USER_PASSWORD_AUTH",
                                    AuthParameters={"USERNAME": username, "PASSWORD": password},)
    token = response["AuthenticationResult"]["IdToken"]
    return token


def API_QUBO(QUBO_matrix, num_reads=100, steps=2000, seed=None):
    username = 'pruizalliata.ieu2022-at-student.ie.edu'
    password = 'deqNob-nysvis-pinni3'
    user_id = '6h7t1fv6nsg0uncgee2o8nl9g9'
    token = login(username, password, user_id)
    URL = 'https://9k53r09joc.execute-api.eu-west-1.amazonaws.com/Prod/'
    ApiKey = 'cY0P09TLMpz6syDZ1mcn5aeLhJm2Dnun32VXx100'
    headers = {
        'x-api-key': ApiKey,
        'Authorization': token
    }
    URL = 'https://9k53r09joc.execute-api.eu-west-1.amazonaws.com/Prod/'

    headers = {
        'x-api-key': ApiKey,
        'Authorization': token
    }
    post_data = {'matrix': QUBO_matrix.tolist(),
                 'shots': str(num_reads),
                 'steps': str(steps)}

    r = requests.post(url=URL+'qubo_sa', json=json.loads(json.dumps(post_data)), headers=headers)
    result = r.json()
    return result['solution'],result['cost']


def graph1(waiter_connections):
    G = nx.Graph()

    for a_table in range(1, 21):
        G.add_node(f'T{a_table}', color = 'red', size = 500)
    for waiter in waiter_connections:
        G.add_node(waiter, color = 'green', size = 1000)

    for waiter, all_tables in waiter_connections.items():
        for a_table in all_tables:
            G.add_edge(waiter, f'T{a_table}')

    waiters = [node for node in G.nodes() if node.startswith('W')]
    tables = [node for node in G.nodes() if node.startswith('T')]

    pos = {}
    theta = np.linspace(0, 2 * np.pi, len(waiters) + 1)[:-1]
    for i, waiter in enumerate(waiters):
        pos[waiter] = np.array([np.cos(theta[i]), np.sin(theta[i])])

    theta = np.linspace(0, 2 * np.pi, len(tables) + 1)[:-1]
    for i, table in enumerate(tables):
        pos[table] = np.array([np.cos(theta[i]), np.sin(theta[i])]) * 2

    node_colors = []
    for _, data in G.nodes(data=True):
        node_colors.append(data['color'])

    node_sizes = [data['size'] for _, data in G.nodes(data=True)]
    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.5, edge_color='gray')
    plt.axis('off')
    return G, pos, node_colors, node_sizes


def graph2(waiter_connections, final_sol, tables_to_serve):
    G = nx.Graph()

    for a_table in range(1, 21):
        color = 'blue' if a_table in tables_to_serve else 'red'
        G.add_node(f'T{a_table}', color=color, size=500)

    for waiter in waiter_connections:
        color = 'yellow' if waiter in final_sol else 'green'
        G.add_node(waiter, color=color, size=1000)

        if waiter in final_sol:
            for a_table in waiter_connections[waiter]:
                G.add_edge(waiter, f'T{a_table}')

    waiters = [node for node in G.nodes() if node.startswith('W')]
    tables = [node for node in G.nodes() if node.startswith('T')]

    pos = {}
    theta = np.linspace(0, 2 * np.pi, len(waiters) + 1)[:-1]
    for i, waiter in enumerate(waiters):
        pos[waiter] = np.array([np.cos(theta[i]), np.sin(theta[i])])

    theta = np.linspace(0, 2 * np.pi, len(tables) + 1)[:-1]
    for i, table in enumerate(tables):
        pos[table] = np.array([np.cos(theta[i]), np.sin(theta[i])]) * 2

    node_colors = [data['color'] for _, data in G.nodes(data=True)]
    node_sizes = [data['size'] for _, data in G.nodes(data=True)]
    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.5, edge_color='gray')
    plt.axis('off')
    return G, pos, node_colors, node_sizes
    
    
def draw_graphs(waiter_connections, final_sol, tables_to_serve):
    G1, pos1, node_colors1, node_sizes1 = graph1(waiter_connections)
    G2, pos2, node_colors2, node_sizes2 = graph2(waiter_connections, final_sol, tables_to_serve)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    nx.draw_networkx_nodes(G1, pos1, node_color=node_colors1, node_size=node_sizes1, ax=ax1)
    nx.draw_networkx_labels(G1, pos1, font_size=10, font_family='sans-serif', ax=ax1)
    nx.draw_networkx_edges(G1, pos1, width=1, alpha=0.5, edge_color='gray', ax=ax1)
    ax1.axis('off')
    ax1.set_title("All Connections")
    nx.draw_networkx_nodes(G2, pos2, node_color=node_colors2, node_size=node_sizes2, ax=ax2)
    nx.draw_networkx_labels(G2, pos2, font_size=10, font_family='sans-serif', ax=ax2)
    nx.draw_networkx_edges(G2, pos2, width=1, alpha=0.5, edge_color='gray', ax=ax2)
    ax2.axis('off')
    ax2.set_title("Solution")

    plt.show()
    

def create_circle(win, center, radius, color, label):
    circle = Circle(center, radius)
    circle.setFill(color)
    circle.draw(win)
    text = Text(center, label)
    text.setSize(10)
    text.draw(win)
    return circle, text

def create_button(win, center, radius, color, label):
    button = Circle(center, radius)
    button.setFill(color)
    button.draw(win)
    text = Text(center, label)
    text.setSize(10)
    text.draw(win)
    return button, text
    
def highlight_waiters_for_table(table_number, waiters, waiter_connections, connections_texts, selected_table):
    for waiter_key, connected_tables in waiter_connections.items():
        connection_text = connections_texts[int(waiter_key[1:]) - 1]
        if selected_table is not None and table_number in connected_tables:
            connection_text.setTextColor("yellow")
        else:
            connection_text.setTextColor("black")
            
def interface(array1, array2, waiter_connections):
    win = GraphWin("Waiter Game", 1000, 600)
    win.setCoords(-250, -350, 650, 250)
    
    colors = [
    "saddlebrown",
    "white",
    "crimson",
    "darkorange",
    "forestgreen",
    "slateblue",
    "darkmagenta",
    "deepskyblue",
    "firebrick",
    "khaki",
    "mediumorchid",
    "midnightblue",
    "palegreen",
    "royalblue",
    "salmon",
    "seagreen",
    "steelblue",
    "violet",
    "goldenrod",
    "darkslategray"
    ]
    
        
    waiters = []
    for i in range(12):
        angle = 2 * 3.141592 * i / 12
        x, y = 100 * math.cos(angle), 100 * math.sin(angle)
        waiter = create_button(win, Point(x, y), 20, "green", f"W{i + 1}")
        waiters.append(waiter)
        
    tables = []
    for i in range(20):
        angle = 2 * 3.141592 * i / 20
        x, y = 200 * math.cos(angle), 200 * math.sin(angle)
        circle, text = create_circle(win, Point(x, y), 25, "red", "")
        tables.append((circle, text))
    
    connections_texts = []
    for i in range(12):
        x, y = 325, -40 * i + 200
        connection_text = Text(Point(x, y), "Waiter " + str(i + 1) + ":")
        connection_text.setSize(20)
        connection_text.draw(win)
        connections_texts.append(connection_text)

        for j in range(5):
            circle = create_circle(win, Point(x + 15 + 40 * (j + 1), y), 10, colors[waiter_connections["W" + str(i + 1)][j] - 1], "")
            
    for i in range(20):
        angle = 2 * 3.141592 * i / 20
        x, y = 200 * math.cos(angle), 200 * math.sin(angle)
        circle, text = create_circle(win, Point(x, y), 15, colors[i], f"T{i + 1}")
        
    
    see_solution_button = Rectangle(Point(-55, -310), Point(55, -260))
    see_solution_button.setFill("grey")
    see_solution_button.draw(win)
    see_solution_text = Text(Point(0, -285), "See Solution")
    see_solution_text.setSize(20)
    see_solution_text.draw(win)


    table_numbers = array1
    waiter_numbers = array2

    for table_number in table_numbers:
        tables[table_number - 1][0].setFill("blue")
        
            
    # Store the original colors for tables
    original_colors = [circle.config['fill'] for circle, _ in tables]
    
    while True:
        click_point = win.getMouse()
        if -50 <= click_point.getX() <= 50 and -310 <= click_point.getY() <= -260:
            break

        clicked_waiter = False
        for i, (circle, _) in enumerate(waiters):
            if circle.getP1().getX() <= click_point.getX() <= circle.getP2().getX() and \
                    circle.getP1().getY() <= click_point.getY() <= circle.getP2().getY():
                clicked_waiter = True
                if circle.config["fill"] == "green":
                    circle.setFill("yellow")
                else:
                    circle.setFill("green")

        selected_table = None

        if not clicked_waiter:
            for i, (circle, _) in enumerate(tables):
                if circle.getP1().getX() <= click_point.getX() <= circle.getP2().getX() and \
                        circle.getP1().getY() <= click_point.getY() <= circle.getP2().getY():

                    # Change the big circle color to yellow if it's not yellow, otherwise change it back to the original color
                    if circle.config['fill'] != 'yellow':
                        circle.setFill('yellow')
                        selected_table = i + 1
                    else:
                        circle.setFill(original_colors[i])
                        selected_table = None

                    highlight_waiters_for_table(i + 1, waiters, waiter_connections, connections_texts, selected_table)
                    break
                    
    for i, (circle, _) in enumerate(waiters):
        circle.setFill("green")
        win.update()  # Add this line to update the color of the waiters
        time.sleep(0.2)
    for i, (circle, _) in enumerate(waiters):
        if str(i + 1) in waiter_numbers:  # Change the comparison to str(i + 1)
            circle.setFill("yellow")
            win.update()  # Add this line to update the color of the waiters
            time.sleep(0.2)
        
        
    win.getMouse()
    win.close()
    plt.close()
    
    
def send_arrays(array1, array2):
    # Replace with the actual serial port name for your Arduino
    serial_port = serial.Serial('/dev/cu.usbmodem2017_2_251', 9600)
    time.sleep(5)  # Give some time for the serial connection to initialize
    array1_str = ",".join(map(str, array1))
    array2_str = ",".join(map(str, array2))

    data = f"{array1_str}|{array2_str}\n"
    print(data)
    serial_port.write(data.encode())
    serial_port.close()
    
def final():
    # which waiter connected to which table
    waiter_connections = {
        'W1': [1, 6, 11, 16, 2],
        'W2': [7, 12, 17, 3, 8],
        'W3': [13, 18, 4, 9, 14],
        'W4': [19, 5, 10, 15, 20],
        'W5': [1, 7, 13, 19, 3],
        'W6': [9, 15, 2, 8, 14],
        'W7': [20, 4, 10, 16, 5],
        'W8': [11, 17, 6, 12, 18],
        'W9': [2, 7, 12, 17, 4],
        'W10': [9, 14, 1, 6, 11],
        'W11': [16, 3, 8, 13, 18],
        'W12': [19, 5, 10, 15, 20],
    }
    # create a set of all the tables
    tables = set(t for connections in waiter_connections.values() for t in connections)
    
    # create a list of waiter sets
    waiter_sets = list(waiter_connections.values())
    V1 = [list(connections) for connections in waiter_sets]
    
    # randomise process, amount of tables and which one to serve
    num_tables_to_serve = random.randint(6, 12)
    tables_to_serve = random.sample(tables, num_tables_to_serve)
    
    
    U = set(tables_to_serve)  #format for library
    V = create_v(V1, tables_to_serve) #format for library
    problem = SetCover(U, V) #transform in set cover problem
    Q = problem.to_qubo() # Create a Qubo problem
    del Q[()]
    Q_mat=qubo_to_matrix(Q) #Create QUbo/hamiltonian Matrix

    x,cost=API_QUBO(Q_mat,num_reads=10) #we use the API  of IQ-Xtreme
    x_array=np.array(x)

    interpretation_sol = problem.convert_solution(x_array) #convert the solution in which table are the one to be selected
    final_sol=["W"+str(x + 1) for x in interpretation_sol]
    
    

    #Replace with your actual arrays
    array1 = tables_to_serve
    array2 = [str(x + 1) for x in interpretation_sol]
    print(array1)
    print(array2)
    return array1, array2, waiter_connections, final_sol, tables_to_serve
    
    
def main():
    
    while True:
        array1, array2, waiter_connections, final_sol, tables_to_serve = final()
        user_input = int(input("Please enter either 1 (Arduino) or 2 (Interface): "))
        if user_input == 1:
            send_arrays(array1, array2)
            draw_graphs(waiter_connections, final_sol, tables_to_serve)
        elif user_input == 2:
            interface(array1, array2, waiter_connections)
        else:
            print("Invalid input. Please enter either 1 or 2.")
    
    
main()
