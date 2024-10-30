import json

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
    def __init__(self, node_info: dict, label:str):
        self._label = label
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
        speed_of_light = 3 *10**8
        latency = (3 / 2) * self.length / speed_of_light
        return latency


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
                print(f"Line {self.label} does not have a successive element with label {next_node_label}")
        else:
            print(f"Signal reached the end of the path at Line {self.label}


class Network(object):
    def __init__(self):
        pass

    @property
    def nodes(self):
        pass

    @property
    def lines(self):
        pass

    def draw(self):
        pass

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        pass

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        pass

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information):
        pass