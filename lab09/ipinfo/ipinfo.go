package main

import (
	"fmt"
	"net"
)

func maskToDotted(mask net.IPMask) string {
	if len(mask) != 4 {
		return mask.String()
	}
	return fmt.Sprintf("%d.%d.%d.%d", mask[0], mask[1], mask[2], mask[3])
}

func main() {
	interfaces, err := net.Interfaces()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	for _, iface := range interfaces {
		if iface.Flags&net.FlagUp == 0 {
			continue
		}
		
		if iface.Flags&net.FlagLoopback != 0 {
			continue
		}

		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}

		for _, addr := range addrs {
			ipNet, ok := addr.(*net.IPNet)
			if !ok {
				continue
			}
			
			if ipNet.IP.To4() == nil {
				continue
			}

			fmt.Printf("IP-адрес: %s\n", ipNet.IP.String())
			fmt.Printf("Маска: %s\n", maskToDotted(ipNet.Mask))
			fmt.Println()
		}
	}
}
