import random
import ipaddress
from copy import deepcopy


INF = 16


class Route:
    def __init__(self, destination, next_hop, metric):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric

class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neighbors = {}
        self.routing_table = {}

        self.routing_table[ip] = Route(ip, ip, 0)

    def add_neighbor(self, neighbor_ip, cost=1):
        self.neighbors[neighbor_ip] = cost

        self.routing_table[neighbor_ip] = Route(
            neighbor_ip,
            neighbor_ip,
            cost
        )

    def send_table(self):
        return deepcopy(self.routing_table)

    def update_table(self, neighbor_ip, neighbor_table):
        updated = False

        cost_to_neighbor = self.neighbors[neighbor_ip]

        for destination, route in neighbor_table.items():

            if destination == self.ip:
                continue

            new_metric = min(INF, route.metric + cost_to_neighbor)

            if destination not in self.routing_table:
                self.routing_table[destination] = Route(
                    destination,
                    neighbor_ip,
                    new_metric
                )
                updated = True

            else:
                current_route = self.routing_table[destination]

                if new_metric < current_route.metric:
                    self.routing_table[destination] = Route(
                        destination,
                        neighbor_ip,
                        new_metric
                    )
                    updated = True

        return updated

    def print_table(self):
        print(f"\nRouter {self.ip} table:")
        print(f"{'[Source IP]':<18}"
              f"{'[Destination IP]':<18}"
              f"{'[Next Hop]':<18}"
              f"{'[Metric]'}")

        for destination, route in sorted(self.routing_table.items()):
            print(f"{self.ip:<18}"
                  f"{destination:<18}"
                  f"{route.next_hop:<18}"
                  f"{route.metric}")


class Network:
    def __init__(self):
        self.routers = {}

    def add_router(self, router):
        self.routers[router.ip] = router

    def connect(self, ip1, ip2, cost=1):
        self.routers[ip1].add_neighbor(ip2, cost)
        self.routers[ip2].add_neighbor(ip1, cost)

    def simulate_rip(self, max_iterations=100):
        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}")

            updated = False
            updates = []

            for router in self.routers.values():
                for neighbor_ip in router.neighbors:
                    updates.append((
                        neighbor_ip,
                        router.ip,
                        router.send_table()
                    ))

            step = 1
            
            for receiver_ip, sender_ip, table in updates:
                receiver = self.routers[receiver_ip]

                changed = receiver.update_table(sender_ip, table)

                if changed:
                    updated = True
                    print(f"{receiver_ip} updated from {sender_ip}")

                print(f"\nSimulation step {step} of router {receiver_ip} ")
                receiver.print_table()
                step += 1

            if not updated:
                print("\nNetwork converged.")
                break

    def print_all_tables(self):
        for router in self.routers.values():
            router.print_table()


def generate_random_network(num_routers=5):
    network = Network()

    ips = set()

    while len(ips) < num_routers:
        ips.add(str(ipaddress.IPv4Address(random.randint(1, 2**32 - 1))))

    ips = list(ips)

    for ip in ips:
        network.add_router(Router(ip))

    for i in range(num_routers - 1):
        network.connect(ips[i], ips[i + 1], random.randint(1, 3))

    extra_links = random.randint(num_routers, num_routers * 2)

    for _ in range(extra_links):
        a, b = random.sample(ips, 2)

        if b not in network.routers[a].neighbors:
            network.connect(a, b, random.randint(1, 5))

    return network


def main():
    num = int(input("Number of routers: "))
    network = generate_random_network(num)

    network.simulate_rip()
    network.print_all_tables()


if __name__ == "__main__":
    main()