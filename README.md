# CoreMark with Printf Test Library

## 简介
这是一个修改版本的CoreMark基准测试程序，集成了printf_test库，删除了原有的系统调用实现，实现了纯baremetal环境下的性能测试。

## 主要修改

### ✅ 删除的系统调用部分
- **删除HTIF系统调用** - 移除了`syscall()`函数和相关的HTIF接口
- **删除复杂的UART实现** - 移除了原syscalls.c中的UART初始化和调试代码
- **简化退出机制** - 不再使用tohost/fromhost机制，改用WFI指令等待

### ✅ 集成printf_test库
- **kprintf.c/kprintf.h** - 轻量级printf实现，支持%s、%c、%x、%lx、%hx格式
- **简化的UART接口** - 直接使用VCU118风格的UART寄存器操作
- **统一的输出接口** - 所有printf、puts、printstr都通过kprintf实现

### ✅ 保留的核心功能
- **CoreMark基准测试逻辑** - 完整保留所有性能测试算法
- **内存管理函数** - memcpy、memset、strlen等基础函数
- **线程和移植层** - core_portme.c中的时间测量和移植接口

## 文件结构
```
coremark_printf_test/
├── README.md                    # 本文件
├── coremark/                    # CoreMark核心代码
│   ├── core_*.c                # CoreMark算法实现
│   ├── coremark.h              # CoreMark头文件
│   ├── Makefile                # CoreMark构建文件
│   └── coremark.bare.riscv     # 生成的可执行文件
└── riscv64-baremetal/          # RISC-V移植层
    ├── core_portme.c           # 移植层实现
    ├── core_portme.h           # 移植层头文件
    ├── core_portme.mak         # 移植层构建配置
    ├── syscalls.c              # 修改后的系统调用实现
    ├── kprintf.c               # printf测试库
    ├── kprintf.h               # printf测试库头文件
    ├── common.h                # 公共定义
    ├── crt.S                   # 启动汇编代码
    ├── link.ld                 # 链接脚本
    └── include/                # 头文件目录
        ├── platform.h          # 平台定义
        └── ...                 # 其他头文件
```

## 编译方法
```bash
# 1. 激活chipyard环境
conda activate /path/to/chipyard/.conda-env/

# 2. 进入coremark目录
cd coremark_printf_test/coremark

# 3. 编译
make PORT_DIR=../riscv64-baremetal compile

# 4. 清理
make PORT_DIR=../riscv64-baremetal clean
```

## 输出文件
- **coremark.bare.riscv** (24,936 字节) - RISC-V 64位可执行文件
- **ELF格式** - 可用于仿真器或硬件平台

## 程序行为
1. **启动信息** - 输出"=== COREMARK WITH KPRINTF LIBRARY ==="
2. **CoreMark测试** - 执行完整的CoreMark基准测试
3. **结果输出** - 使用kprintf输出测试结果和性能数据
4. **正常退出** - 输出"=== COREMARK TEST COMPLETED SUCCESSFULLY ==="
5. **等待状态** - 进入WFI循环等待复位

## 与原版本对比

| 特性 | 原版本 | 修改版本 |
|------|--------|----------|
| 系统调用 | HTIF/syscall | 已删除 |
| 输出方式 | 复杂UART + HTIF | 简化kprintf |
| 退出方式 | tohost/fromhost | WFI等待 |
| 依赖关系 | 依赖系统调用 | 纯baremetal |
| 代码大小 | 更大 | 更小 |
| 调试信息 | 复杂调试结构 | 简化输出 |

## 使用场景
- **FPGA验证** - 直接在RISC-V硬件上运行性能测试
- **仿真器测试** - 在Spike、QEMU等仿真器中运行
- **Bare-metal开发** - 作为纯硬件环境的基准测试
- **性能分析** - 评估RISC-V处理器的整数运算性能

## 注意事项
- 需要正确设置RISCV环境变量指向工具链
- 目标平台需要支持VCU118风格的UART接口
- 输出格式限制：只支持kprintf的格式符(%s、%c、%x等)
- 内存布局由link.ld链接脚本控制

## 技术细节
- **架构**: RISC-V 64位 (rv64ima)
- **ABI**: lp64
- **编译优化**: -O2
- **链接方式**: 静态链接，无标准库
- **UART地址**: 0x64000000 (VCU118平台)

这个版本保持了CoreMark的核心性能测试功能，同时简化了系统接口，使其更适合在bare-metal环境下运行。 