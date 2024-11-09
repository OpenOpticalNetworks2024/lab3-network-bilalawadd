import json
import math
import matplotlib.pyplot as plt
import pandas as pd

class Signal_information(object):
    def __init__(self, signal_power, path):
        self._signal_power = signal_power
        self._noise_power = 0
        self._latency = 0
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
    def latency(self,latency1: float):
        self._latency = latency1


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
    def __init__(self, node_info: dict,label:str):
        self._label = label
        self._position = node_info.get("position", (0, 0))  # tuple
        self._connected_nodes = node_info.get("connected_nodes", [])
        self._successive = {}  # empty dict

    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, label1):
        self._label = label1

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, position1):
        self._position = position1

    @property
    def connected_nodes(self):
        return self._connected_nodes
    @connected_nodes.setter
    def connected_nodes(self, connected_nodes1):
        self._connected_nodes = connected_nodes1

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self,successive1):
        self._successive = successive1

    def propagate(self, sig: Signal_information):
        for node in sig.path:
            if len(sig.path) > 1:
                if node == self._label:
                    sig.update_path(node)
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
    def label(self, label1):
        self._label = label1

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length1):
        self._length = length1

    @property
    def successive(self):
        return self._successive


    @successive.setter
    def successive(self,successive1):
        self._successive = successive1



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
    nodes: dict[str, Node]
    lines: dict[str, Line]
    def __init__(self,filename):
        self._nodes={}
        self._lines={}
        with open("../resources./nodes.json") as fileHandle:
            data = json.load(fileHandle)
            for jsonNode in data.items():
                node = Node(jsonNode[1], jsonNode[0])
                self.nodes[jsonNode[0]] = node

            for node in self.nodes.values():
                for innerNode in node.connected_nodes:
                    newNode = self.nodes[innerNode]
                    lineLabel = node.label + innerNode
                    line = Line(self.lineLength(node, newNode), lineLabel)
                    self.lines[lineLabel] = line

    def lineLength(self, node1, node2):
        x1, y1 = node1._position
        x2, y2 = node2._position
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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
        # Create a visualization of the network
        plt.figure(figsize=(8, 8))
        for node in self.nodes.values():
            x, y = node.position
            plt.plot(x, y, 'ro')
            plt.text(x, y, node._label, fontsize=12, ha='center')

        for line in self.lines.values():
            node1, node2 = line._label[0], line._label[1]
            x1, y1 = self.nodes[node1].position
            x2, y2 = self.nodes[node2].position
            plt.plot([x1, x2], [y1, y2], 'b-')

        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
        plt.title("Network Diagram")
        plt.grid()
        plt.show()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, start: str, end: str, visited=None, path=None):
        if visited is None:
            visited = set()
        if path is None:
            path = []
        node = self.nodes[start]
        visited.add(node.label)
        path = path + [node.label]

        if node.label == end:
            return [path]

        paths = []
        for line in node.successive.values():
            # next_node_label = line.successive[node.label].label
            next_node_label = list(line.successive.values())[-1].label
            if next_node_label not in visited:
                new_paths = self.find_paths(next_node_label, end, visited.copy(), path.copy())
                paths.extend(new_paths)
        return paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        for nodeLabel, node in self.nodes.items():
            # node.successive = { line.label : line for line in self.lines.values() if nodeLabel in line.label }
            for line in self.lines.values():  # same as the line above
                if nodeLabel == line.label[0]:  # to take just the line straight forward following the path
                    node.successive[line.label] = line

        for lineLabel, line in self.lines.items():
            node1Label, node2label = lineLabel[0], lineLabel[1]
            # line.successive = { nodeLabel : self.nodes[nodeLabel] for nodeLabel in (node1Label, node2label)}
            for nodeLabel in (node1Label, node2label):  # same as the line above
                line.successive[nodeLabel] = self.nodes[nodeLabel]
    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signalInformation: Signal_information):
        self.nodes[signalInformation.path[0]].propagate(signalInformation)

    def results(self):
        all_paths_data = []  # Store all data to avoid row-by-row concatenation

        for node1 in self.nodes.keys():
            for node2 in self.nodes.keys():
                if node1 != node2:
                    paths = self.find_paths(node1, node2)
                    for path in paths:
                        path_string = '->'.join(path)
                        sig = Signal_information(0.001, path)
                        self.propagate(sig)

                        # Calculate SNR in dB
                        SNR = 10 * math.log10(sig.signal_power / sig.noise_power)

                        # Append path information as a dict
                        all_paths_data.append({
                            'Path': path_string,
                            'Accumulated Latency': sig.latency,
                            'Accumulated Noise': sig.noise_power,
                            'SNR (dB)': SNR
                        })

        # Create DataFrame from the collected data in one operation
        df = pd.DataFrame(all_paths_data)
        print(df)