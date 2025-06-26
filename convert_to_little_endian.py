#!/usr/bin/env python3

import sys

def calculate_checksum(data_bytes):
    """计算Intel HEX校验和"""
    checksum = sum(data_bytes) & 0xFF
    return (256 - checksum) & 0xFF

def convert_hex_to_little_endian(input_file, output_file):
    """将Intel HEX文件从大端序转换为真正的小端序"""
    
    print(f"🔄 转换大端序Intel HEX为小端序...")
    print(f"   输入: {input_file}")
    print(f"   输出: {output_file}")
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # 写入文件头
        outfile.write("; RISC-V 真正的小端序 HEX 文件\n")
        outfile.write("; 字节序已从大端序翻转为小端序\n")
        outfile.write(";\n")
        
        data_line_count = 0
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith(';'):
                continue
                
            if not line.startswith(':'):
                outfile.write(line + '\n')
                continue
            
            # 解析Intel HEX行
            if len(line) < 11:
                outfile.write(line + '\n')
                continue
                
            try:
                # 提取字段
                byte_count = int(line[1:3], 16)
                address = int(line[3:7], 16)
                record_type = int(line[7:9], 16)
                
                if record_type == 0x00 and byte_count > 0:  # 数据记录
                    data_line_count += 1
                    
                    # 提取原始数据字节
                    data_hex = line[9:9+byte_count*2]
                    original_bytes = []
                    for i in range(0, len(data_hex), 2):
                        original_bytes.append(int(data_hex[i:i+2], 16))
                    
                    if data_line_count <= 5:  # 只显示前5行的转换过程
                        print(f"   行{data_line_count}: 地址0x{address:04X}")
                        print(f"     原始: {' '.join(f'{b:02X}' for b in original_bytes)}")
                    
                    # 按4字节分组进行字节序翻转
                    converted_bytes = []
                    for i in range(0, len(original_bytes), 4):
                        group = original_bytes[i:i+4]
                        
                        # 如果不足4字节，保持原样
                        if len(group) < 4:
                            converted_bytes.extend(group)
                        else:
                            # 翻转4字节：[a,b,c,d] -> [d,c,b,a]
                            converted_bytes.extend(group[::-1])
                    
                    if data_line_count <= 5:
                        print(f"     转换: {' '.join(f'{b:02X}' for b in converted_bytes)}")
                    
                    # 重新构建Intel HEX行
                    hex_parts = []
                    hex_parts.append(f"{byte_count:02X}")
                    hex_parts.append(f"{address:04X}")
                    hex_parts.append(f"{record_type:02X}")
                    
                    for byte_val in converted_bytes:
                        hex_parts.append(f"{byte_val:02X}")
                    
                    # 计算校验和
                    checksum_data = [byte_count, (address >> 8) & 0xFF, address & 0xFF, record_type] + converted_bytes
                    checksum = calculate_checksum(checksum_data)
                    hex_parts.append(f"{checksum:02X}")
                    
                    new_line = ":" + "".join(hex_parts)
                    outfile.write(new_line + '\n')
                    
                else:
                    # 非数据记录，直接复制
                    outfile.write(line + '\n')
                    
            except (ValueError, IndexError) as e:
                print(f"   警告: 第{line_num}行解析失败: {line}")
                outfile.write(line + '\n')
    
    print(f"✅ 转换完成! 处理了 {data_line_count} 行数据")

def main():
    if len(sys.argv) < 3:
        print("用法: python3 convert_to_little_endian.py <大端序.hex> <小端序.hex>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("🚀 Intel HEX 大端序转小端序工具")
    print("=" * 50)
    
    convert_hex_to_little_endian(input_file, output_file)

if __name__ == "__main__":
    main()
