import json
import math
import matplotlib.pyplot as plt
import pandas as pd
class Signal_information(object):
    def __init__(self, signal_power: float, path: list[str]):
        self._signal_power = signal_power
        self._noise_power = 0.0
        self._latency = 0.0
        self._path = path


    @property
    def signal_power(self):
       return self._signal_power



    def update_signal_power(self,delta_signal_power: float):
       self._signal_power +=delta_signal_power


    @property
    def noise_power(self):
        return self._noise_power


    @noise_power.setter
    def noise_power(self,noise: float):
         self._noise_power = noise


    def update_noise_power(self,delt_noise: float):
        self._noise_power += delt_noise


    @property
    def latency(self):
        return self._latency


    @latency.setter
    def latency(self,latency: float):
        self._latency = latency


    def update_latency(self,delta_latency: float):
        self._latency += delta_latency


    @property
    def path(self):
        return self._path


    @path.setter
    def path(self,anypath):
        if isinstance(anypath, list):  # check if value is a list to assign it to the path
            self._path = anypath


    def update_path(self,node):
        self._path.remove(node)



class Node(object):
    def __init__(self, node_info: dict):
        self._label = node_info.get('label','')
        self._position = node_info.get("position", (0, 0))  # tuple
        self._connected_nodes = node_info.get("connected_nodes", [])
        self._successive = {}  # empty dict

    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, label):
        self._label = label

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, position):
        self._position = position

    @property
    def connected_nodes(self):
        return self._connected_nodes
    @connected_nodes.setter
    def connected_nodes(self, connected_nodes):
        self._connected_nodes = connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self,successive):
        self._successive = successive

    def propagate(self, sig: Signal_information):
        for node in sig.path:
            if sig.path:
                if node == self._label:
                    sig.update_path(node)  # remove the node crossed by the signal
                    line = self.successive[node + sig.path[0]]
                    line.propagate(sig)


class Line(object):
    def __init__(self,length:float, label:str):
        self._length = length
        self._label = label
        self._successive = {}


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._length = length

    @property
    def successive(self):
        return self._successive


    @successive.setter
    def successive(self,successive):
        self._successive = successive



    def latency_generation(self):
        speed_in_fiber = 2 * 10 ** 8  # Speed of light in fiber (m/s)
        return self._length / speed_in_fiber

    def noise_generation(self,signal_power):
       noise_power = 1e-9 * signal_power * self.length
       return noise_power


    def propagate(self,new_signal_info):
        noise = self.noise_generation(new_signal_info.signal_power)
        new_signal_info.update_noise_power(noise)
        latency = self.latency_generation()
        new_signal_info.update_latency(latency)

        # Check if there is a successive node along the specified path

        if new_signal_info.path:
            next_node_label = new_signal_info.path[0]
            if next_node_label in self.successive:
                next_node = self.successive[next_node_label]
                next_node.propagate(new_signal_info)
            else:
                print(f"Line {self.label} doesnt have a successive element with label {next_node_label}")
        else:
            print(f"Signal reached the end of the path at {self.label}")


class Network(object):
    def __init__(self,filename: str):
        self._nodes={}
        self._lines={}
        with open(filename, 'r') as fileHandle:
            node_data = json.load(fileHandle)

            # Create Node instances
        for node_label, attributes in node_data.items():
            position = tuple(attributes['position'])
            connected_nodes = attributes['connected_nodes']
            # Instantiate Node and add to nodes dictionary
            self._nodes[node_label] = Node({
            'label': node_label,
            'position': position,
             'connected_nodes': connected_nodes
             })
        for node in self.nodes.values():
            for innerNode in node.connected_nodes:
                newNode = self.nodes[innerNode]
                lineLabel = node.label + innerNode
                line = Line(self.lineLength(node, newNode), lineLabel)
                self.lines[lineLabel] = line

    def lineLength(self, node1, node2):
        pos1, pos2 = node1.position, node2.position
        return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, new_nodes: dict):
        if isinstance(new_nodes, dict):
            self._nodes = new_nodes

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, new_lines: dict):
        if isinstance(new_lines, dict):
            self._lines = new_lines

    def draw(self):
        plt.figure(figsize=(8, 6))

        # Draw nodes
        for node_label, node in self.nodes.items():
            x, y = node.position
            plt.plot(x, y, 'o', markersize=8, color='blue')
            plt.text(x, y, f'{node_label}', fontsize=12, ha='right', color='darkblue')

        # Draw lines
        for line_label, line in self.lines.items():
            start_node_label, end_node_label = line_label[0], line_label[1]
            start_pos = self.nodes[start_node_label].position
            end_pos = self.nodes[end_node_label].position
            plt.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 'k-', linewidth=1)
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            plt.text(mid_x, mid_y, f'{line_label}', fontsize=10, color='green')

        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.title("Network Visualization")
        plt.grid(True)
        plt.show()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, start, end, path=None):
        if path is None:
            path = []
        path = path + [start]
        if start == end:
            return [path]

        paths = []
        for node_label in self.nodes[start].connected_nodes:
            if node_label not in path:
                new_paths = self.find_paths(node_label, end, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        # Assign each line a destination node
        for line in self.lines.values():
            start_node, end_node = line.label[0], line.label[1]
            if start_node in self.nodes and end_node in self.nodes:
                line.successive[end_node] = self.nodes[end_node]

        # Assign each node a dictionary of outgoing lines
        for node in self.nodes.values():
            for connected_node_label in node.connected_nodes:
                line_label = ''.join(sorted([node.label, connected_node_label]))
                if line_label in self.lines:
                    node.successive[line_label] = self.lines[line_label]

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, sig_info: Signal_information):
        self.nodes[sig_info.path[0]].propagate(sig_info)