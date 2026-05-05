package main

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"sync"
	"time"
)

func main() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: go run scanner.go <IP-address> <start_port> <end_port>")
		os.Exit(1)
	}

	ip := os.Args[1]
	startPort, err := strconv.Atoi(os.Args[2])
	if err != nil {
		fmt.Printf("Error: invalid start port '%s'\n", os.Args[2])
		os.Exit(1)
	}

	endPort, err := strconv.Atoi(os.Args[3])
	if err != nil {
		fmt.Printf("Error: invalid end port '%s'\n", os.Args[3])
		os.Exit(1)
	}

	if startPort < 1 || endPort > 65535 || startPort > endPort {
		fmt.Println("Error: ports must be in range 1-65535, and start port cannot be greater than end port")
		os.Exit(1)
	}

	ipAddr, err := resolveIP(ip)
	if err != nil {
		fmt.Printf("Error: failed to resolve IP address '%s': %v\n", ip, err)
		os.Exit(1)
	}

	fmt.Printf("Scanning ports for %s (%s) in range %d-%d...\n", ip, ipAddr, startPort, endPort)

	openPorts := scanPorts(ipAddr, startPort, endPort)

	if len(openPorts) == 0 {
		fmt.Printf("No open ports found in range %d-%d\n", startPort, endPort)
	} else {
		fmt.Printf("Found %d open ports:\n", len(openPorts))
		for _, port := range openPorts {
			fmt.Printf("  %d\n", port)
		}
	}
}

func resolveIP(host string) (string, error) {
	if net.ParseIP(host) != nil {
		return host, nil
	}

	ips, err := net.LookupIP(host)
	if err != nil {
		return "", err
	}

	for _, ip := range ips {
		if ipv4 := ip.To4(); ipv4 != nil {
			return ipv4.String(), nil
		}
	}

	if len(ips) > 0 {
		return ips[0].String(), nil
	}

	return "", fmt.Errorf("failed to resolve hostname")
}

func scanPorts(ip string, startPort, endPort int) []int {
	var wg sync.WaitGroup
	var mu sync.Mutex
	openPorts := []int{}

	semaphore := make(chan struct{}, 100)
	
	for port := startPort; port <= endPort; port++ {
		wg.Add(1)
		go func(p int) {
			defer wg.Done()
			
			semaphore <- struct{}{}
			defer func() { <-semaphore }()
			
			if isPortOpen(ip, p) {
				mu.Lock()
				openPorts = append(openPorts, p)
				mu.Unlock()
			}
		}(port)
	}
	
	wg.Wait()
	return openPorts
}

func isPortOpen(ip string, port int) bool {
	address := fmt.Sprintf("%s:%d", ip, port)
	
	conn, err := net.DialTimeout("tcp", address, 500*time.Millisecond)
	if err != nil {
		return false
	}
	defer conn.Close()
	
	return true
}