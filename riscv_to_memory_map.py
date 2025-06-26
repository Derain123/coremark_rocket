#!/usr/bin/env python3

import subprocess
import sys
import os
import re

class RiscvToMemoryMap:
    def __init__(self, objcopy_path="/home/rain/chipyard/.conda-env/riscv-tools/bin/riscv64-unknown-elf-objcopy"):
        self.objcopy_path = objcopy_path
    
    def step1_elf_to_hex(self, elf_file, hex_file):
        """
        第一步：将RISC-V ELF文件转换为Intel HEX文件
        """
        try:
            print(f"第一步：转换 {elf_file} -> {hex_file}")
            
            # 使用objcopy将ELF转为Intel HEX格式
            cmd = [self.objcopy_path, "-O", "ihex", elf_file, hex_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"错误：objcopy执行失败: {result.stderr}")
                return False
            
            print(f"✅ 成功生成HEX文件: {hex_file}")
            return True
            
        except Exception as e:
            print(f"错误：第一步失败 - {e}")
            return False
    
    def step2_ensure_little_endian_hex(self, input_hex, output_hex):
        """
        第二步：确保HEX文件是小端序格式（RISC-V标准）
        对于RISC-V，数据已经是小端序，这一步主要是验证和可选的重新组织
        """
        try:
            print(f"第二步：处理小端序格式 {input_hex} -> {output_hex}")
            
            with open(input_hex, 'r') as infile, open(output_hex, 'w') as outfile:
                # 添加说明头
                outfile.write("; RISC-V 小端序 HEX 文件\n")
                outfile.write("; 从ELF文件转换而来，保持RISC-V原生小端序格式\n")
                outfile.write(";\n")
                
                for line in infile:
                    line = line.strip()
                    if line:
                        # 直接复制Intel HEX格式的行
                        # RISC-V objcopy已经输出正确的小端序格式
                        outfile.write(line + "\n")
            
            print(f"✅ 小端序HEX文件处理完成: {output_hex}")
            return True
            
        except Exception as e:
            print(f"错误：第二步失败 - {e}")
            return False
    
    def step3_hex_to_memory_map(self, hex_file, map_file, start_address=0x80000000):
        """
        第三步：将HEX文件转换为地址映射表
        """
        try:
            print(f"第三步：生成地址映射表 {hex_file} -> {map_file}")
            
            # 解析Intel HEX文件
            memory_data = {}
            current_base_address = 0
            
            with open(hex_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                    
                    if not line.startswith(':'):
                        continue
                    
                    try:
                        # 解析Intel HEX格式
                        # :llaaaatt[dd...]cc
                        # ll = 数据长度, aaaa = 地址, tt = 类型, dd = 数据, cc = 校验和
                        
                        record = line[1:]  # 去掉':'
                        if len(record) < 8:
                            continue
                            
                        byte_count = int(record[0:2], 16)
                        address = int(record[2:6], 16)
                        record_type = int(record[6:8], 16)
                        
                        if record_type == 0x00:  # 数据记录
                            data_start = 8
                            for i in range(byte_count):
                                if data_start + 2 <= len(record) - 2:  # 减去校验和
                                    byte_data = record[data_start:data_start+2]
                                    memory_address = current_base_address + address + i
                                    memory_data[memory_address] = int(byte_data, 16)
                                    data_start += 2
                        
                        elif record_type == 0x04:  # 扩展线性地址记录
                            if byte_count == 2 and len(record) >= 12:
                                high_address = int(record[8:12], 16)
                                current_base_address = high_address << 16
                        
                        elif record_type == 0x05:  # 起始线性地址记录
                            if byte_count == 4 and len(record) >= 16:
                                start_addr = int(record[8:16], 16)
                                print(f"   检测到起始地址: 0x{start_addr:08X}")
                    
                    except ValueError as e:
                        print(f"   警告: 第{line_num}行解析失败: {line}")
                        continue
            
            # 生成地址映射表
            with open(map_file, 'w') as f:
                f.write("RISC-V 小端序内存地址映射表\n")
                f.write("=" * 60 + "\n")
                f.write("地址格式: 每4字节(32位)一行，小端序排列\n")
                f.write(f"起始地址: 0x{start_address:08X}\n")
                f.write("=" * 60 + "\n\n")
                
                # 按地址排序并按4字节对齐输出
                sorted_addresses = sorted(memory_data.keys())
                
                if sorted_addresses:
                    # 找到实际的起始地址，通常应该与start_address一致
                    actual_start = sorted_addresses[0] & 0xFFFFFFFC  # 4字节对齐
                    
                    # 从对齐的起始地址开始，每4字节输出一行
                    current_addr = actual_start
                    max_addr = sorted_addresses[-1]
                    
                    while current_addr <= max_addr:
                        # 收集4个字节
                        bytes_data = []
                        for i in range(4):
                            addr = current_addr + i
                            if addr in memory_data:
                                bytes_data.append(memory_data[addr])
                            else:
                                bytes_data.append(0)  # 未定义区域填充0
                        
                        # 小端序：低位字节在前
                        word_value = (bytes_data[3] << 24) | (bytes_data[2] << 16) | (bytes_data[1] << 8) | bytes_data[0]
                        
                        f.write(f"{current_addr:08X}: {word_value:08X}\n")
                        current_addr += 4
                
                f.write(f"\n" + "=" * 60 + "\n")
                f.write(f"总共输出 {(max_addr - actual_start + 4) // 4} 个32位字\n")
                f.write("格式说明: 地址:数据值 (小端序)\n")
            
            print(f"✅ 地址映射表生成完成: {map_file}")
            print(f"   地址范围: 0x{actual_start:08X} - 0x{max_addr:08X}")
            return True
            
        except Exception as e:
            print(f"错误：第三步失败 - {e}")
            return False
    
    def convert_all(self, elf_file, base_name=None):
        """
        执行完整的三步转换流程
        """
        if base_name is None:
            base_name = os.path.splitext(os.path.basename(elf_file))[0]
        
        # 生成文件名
        step1_hex = f"{base_name}_step1.hex"
        step2_hex = f"{base_name}_little_endian.hex"  
        step3_map = f"{base_name}_memory_map.txt"
        
        print("🚀 开始RISC-V文件三步转换流程")
        print("=" * 50)
        
        # 第一步：ELF -> HEX
        if not self.step1_elf_to_hex(elf_file, step1_hex):
            return False
        
        # 第二步：确保小端序HEX格式
        if not self.step2_ensure_little_endian_hex(step1_hex, step2_hex):
            return False
        
        # 第三步：HEX -> 地址映射表
        if not self.step3_hex_to_memory_map(step2_hex, step3_map):
            return False
        
        print("\n🎉 三步转换全部完成！")
        print("=" * 50)
        print(f"📁 生成的文件:")
        print(f"   1. Intel HEX文件: {step1_hex}")
        print(f"   2. 小端序HEX文件: {step2_hex}")
        print(f"   3. 地址映射表: {step3_map}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("用法: python3 riscv_to_memory_map.py <RISC-V ELF文件> [输出基础名]")
        print("示例: python3 riscv_to_memory_map.py coremark.bare.riscv")
        print("      python3 riscv_to_memory_map.py coremark.bare.riscv my_output")
        sys.exit(1)
    
    elf_file = sys.argv[1]
    base_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(elf_file):
        print(f"错误: 文件不存在 {elf_file}")
        sys.exit(1)
    
    converter = RiscvToMemoryMap()
    success = converter.convert_all(elf_file, base_name)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 