package main

func ComputeChecksum(data []byte) uint16 {
	var sum uint32
	length := len(data)
	
	for i := 0; i+1 < length; i += 2 {
		word := uint32(data[i])<<8 | uint32(data[i+1])
		sum += word
		if sum & 0xFFFF0000 != 0 {
			sum = (sum & 0xFFFF) + 1
		}
	}
	
	if length % 2 == 1 {
		word := uint32(data[length-1]) << 8
		sum += word
		if sum&0xFFFF0000 != 0 {
			sum = (sum & 0xFFFF) + 1
		}
	}
	
	return ^uint16(sum & 0xFFFF)
}

func VerifyChecksum(data []byte, checksum uint16) bool {
	var sum uint32
	length := len(data)
	
	for i := 0; i+1 < length; i += 2 {
		word := uint32(data[i])<<8 | uint32(data[i+1])
		sum += word
		if sum & 0xFFFF0000 != 0 {
			sum = (sum & 0xFFFF) + 1
		}
	}
	
	if length % 2 == 1 {
		word := uint32(data[length-1]) << 8
		sum += word
		if sum&0xFFFF0000 != 0 {
			sum = (sum & 0xFFFF) + 1
		}
	}
	
	sum += uint32(checksum)
	if sum & 0xFFFF0000 != 0 {
		sum = (sum & 0xFFFF) + 1
	}
	
	return (sum & 0xFFFF) == 0xFFFF
}
