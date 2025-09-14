from typing import Dict

import bits

class AddressOutOfRange(Exception):
    def __init__(self, addr: int, upper: int):
        self.message = f"Address {addr} out of range [0, {upper}]"
        super().__init__(self.message)


class SignedUnderflow(Exception):
    def __init__(self, data: int, width: int):
        m = bits.signed_min(width)
        self.message = f"Value {data} less than minimum signed value {m}."
        super().__init__(self.message)


class SignedOverflow(Exception):
    def __init__(self, data: int, width: int):
        M = bits.signed_max(width)
        self.message = f"Value {data} more than maximum signed value {M}."
        super().__init__(self.message)


class UnsignedUnderflow(Exception):
    def __init__(self, data: int, width: int):
        m = bits.unsigned_min()
        self.message = f"Value {data} less than minimum unsigned value {m}."
        super().__init__(self.message)


class UnsignedOverflow(Exception):
    def __init__(self, data: int, width: int):
        M = bits.unsigned_max(width)
        self.message = f"Value {data} more than maximum unsigned value {M}."
        super().__init__(self.message)


class InvalidRange(Exception):
    def __init__(self, min: int, max: int):
        self.message = f"Invalid range: min: {min}, max: {max}."
        super().__init__(self.message)


class RAM:
    def __init__(self, width: int, addr_width: int) -> None:
        """Initialise the RAM with specified `width` and `address width`.

        Args:
            width (int): Width in bits for each memory cell
            addr_width (int): Log2 of the number of such memory cells
        """
        self.width = width
        self.depth: int = 2 ** addr_width
        self.addr_width = addr_width
        
        self.data : Dict[int, int] = {}
    
    
    def _verify_address(self, address: int, addrMax: int) -> None:
        """Verify that the `address` lies within `0...addrMax`.

        Raises:
            AddressOutOfRange: Address does not lie in the specified range.
        """
        if not (0 <= address <= addrMax):
            raise AddressOutOfRange(address, addrMax)
        return None
    
    
    def _verify_data(self, data: int, width: int) -> None:
        """Verify that `data` fits in `width` bits.
        
        Raises:
            UnsignedUnderflow: If `data` is less than `0`
            UnsignedOverflow: If `data` is more than `2^width - 1`
        """
        if data < 0:
            raise UnsignedUnderflow(data, width)
        
        if data > bits.unsigned_max(width):
            raise UnsignedOverflow(data, width)
    
    
    def read_byte(self, address: int) -> int:
        """Reads one byte at the given `address`.

        Raises:
            AddressOutOfRange: If `address` is out of range for the RAM

        Returns:
            int: Data stored at address
        """
        self._verify_address(address, self.depth - 1)

        if address in self.data:
            return self.data[address]        
        return 0
    
    
    def write_byte(self, address: int, data: int) -> None:
        """Writes one byte `data` at the given `address`.

        Raises:
            AddressOutOfRange: If `address` is out of range for the RAM
            UnsignedUnderflow: If `data` is less than `0`
            UnsignedOverflow: If `data` is more than `2^width - 1`
        """
        self._verify_address(address, self.depth - 1)

        self._verify_data(data, self.width)

        if data == 0:
            self.data.pop(address, None)
        else:
            self.data[address] = data
        return None
    
            
    def read_word(self, address: int) -> int:
        """Reads 4 bytes of data at starting at the givn `address`.

        Raises:
            AddressOutOfRange: If `address` is out of range for the RAM

        Returns:
            int: Data stored in the word starting at `address`
        """
        self._verify_address(address, self.depth - 4)
        
        data: int = 0
            
        for i in range(4):
            byte = self.read_byte(address + i)
            data |= byte << (i * self.width)
        
        return data
    
    
    def write_word(self, address: int, data: int) -> None:
        """Writes 4 bytes of `data`, starting at the given `address`.

        Raises:
            AddressOutOfRange: If `address` is out of range for the RAM
            UnsignedUnderflow: If `data` is less than `0`
            UnsignedOverflow: If `data` is more than `2^(width*4) - 1`
        """
        self._verify_address(address, self.depth - 4)
        self._verify_data(data, self.width * 4)

        mask = bits.unsigned_max(self.width)
        
        for i in range(4):
            byte = (data >> (i * self.width)) & mask
            self.write_byte(address + i, byte)

        return None
    
    
    def clear(self) -> None:
        """Clear the contents of the RAM"""
        self.data.clear()
    
    
    def load(self, data: bytes, base_addr: int) -> None:
        for offset, byte in enumerate(data):
            self.write_byte(base_addr + offset, byte)
    
    
    def print_words(self, minAddr: int, maxAddr: int) -> None:
        if minAddr > maxAddr:
            raise InvalidRange(minAddr, maxAddr)

        minWordAddr = minAddr - (minAddr % 4)            
        maxWordAddr = maxAddr - (maxAddr % 4)

        for wordAddr in reversed(range(minWordAddr, 1 + maxWordAddr, 4)):
            hexWordAddr = hex(wordAddr)[2:].zfill(self.addr_width // 4)
            
            print(f"{hexWordAddr}: ", end='')
            
            for i in reversed(range(4)):
                byte = self.read_byte(wordAddr + i)
                hexByte = hex(byte)[2:].zfill(2)
                print(f"{hexByte}", end=' ')

            print("")
    