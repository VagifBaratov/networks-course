package main

import (
	"math/rand"
	"testing"
	"time"
)

func TestEmptyData(t *testing.T) {
	data := []byte{}
	cs := ComputeChecksum(data)
	
	expected := uint16(0xFFFF)
	
	if cs != expected {
		t.Errorf("Пустые данные: ожидается 0x%04X, получено 0x%04X", expected, cs)
	}
	
	if !VerifyChecksum(data, cs) {
		t.Error("Проверка для пустых данных должна быть успешной")
	}
}

func TestEvenLength(t *testing.T) {
	data := []byte{0x01, 0x02, 0x03, 0x04}
	cs := ComputeChecksum(data)

	expected := uint16(0xFBF9)
	
	if cs != expected {
		t.Errorf("Чётные данные (4 байта): ожидается 0x%04X, получено 0x%04X", expected, cs)
	}
	
	if !VerifyChecksum(data, cs) {
		t.Error("Проверка должна быть успешной для корректных данных")
	}
	
	corrupted := make([]byte, len(data))
	copy(corrupted, data)
	corrupted[2] ^= 0x80
	
	if VerifyChecksum(corrupted, cs) {
		t.Error("Проверка должна обнаружить ошибку в повреждённых данных")
	}
}

func TestOddLength(t *testing.T) {
	data := []byte{0x11, 0x22, 0x33}
	cs := ComputeChecksum(data)
	
	expected := uint16(0xBBDD)
	
	if cs != expected {
		t.Errorf("Нечётные данные (3 байта): ожидается 0x%04X, получено 0x%04X", expected, cs)
	}
	
	if !VerifyChecksum(data, cs) {
		t.Error("Проверка должна быть успешной для корректных данных")
	}
}

func TestMultipleOverflows(t *testing.T) {
	data := make([]byte, 100)
	for i := 0; i < len(data); i += 2 {
		data[i] = 0xFF
		data[i+1] = 0xFF
	}
	
	cs := ComputeChecksum(data)
	
	if !VerifyChecksum(data, cs) {
		t.Error("Проверка должна быть успешной для данных с переполнениями")
	}
}

func TestSingleBitErrors(t *testing.T) {
	original := []byte{0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC}
	cs := ComputeChecksum(original)

	for bytePos := 0; bytePos < len(original); bytePos++ {
		for bit := 0; bit < 8; bit++ {
			corrupted := make([]byte, len(original))
			copy(corrupted, original)
			corrupted[bytePos] ^= 1 << bit
			
			if VerifyChecksum(corrupted, cs) {
				t.Errorf("Однобитовая ошибка не обнаружена: позиция байта %d, бит %d", bytePos, bit)
			}
		}
	}
}

func TestMaxSize(t *testing.T) {
	const L = 65535
	data := make([]byte, L)
	for i := 0; i < L; i++ {
		data[i] = byte(i % 256)
	}
	
	cs := ComputeChecksum(data)
	
	if !VerifyChecksum(data, cs) {
		t.Error("Проверка для максимального размера данных не прошла")
	}
	
	data[L/2] ^= 0xFF
	
	if VerifyChecksum(data, cs) {
		t.Error("Ошибка не обнаружена")
	}
}

func TestRandomData(t *testing.T) {
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	
	for test := 0; test < 100; test++ {
		length := rng.Intn(1000) + 1
		data := make([]byte, length)
		
		for i := range data {
			data[i] = byte(rng.Intn(256))
		}
		
		cs := ComputeChecksum(data)
		
		if !VerifyChecksum(data, cs) {
			t.Errorf("Сбой для случайных данных длины %d", length)
		}
	
		if len(data) > 0 {
			corrupted := make([]byte, len(data))
			copy(corrupted, data)
			pos := rng.Intn(len(data))
			corrupted[pos] ^= 0x01
			
			if VerifyChecksum(corrupted, cs) {
				t.Errorf("Ошибка не обнаружена для повреждённых данных (длина %d, позиция %d)", length, pos)
			}
		}
	}
}