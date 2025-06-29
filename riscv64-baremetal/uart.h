#ifndef __UART_H
#define __UART_H

#include <stdint.h>

// UART基地址 - 根据具体平台调整
// 这里使用常见的地址，实际使用时需要根据硬件平台修改
#ifndef UART_BASE
#define UART_BASE       0x10000000UL
#endif

// 16550兼容UART寄存器偏移
#define UART_THR        0x00    // 发送保持寄存器 (Transmit Holding Register)
#define UART_RBR        0x00    // 接收缓冲寄存器 (Receive Buffer Register)
#define UART_IER        0x01    // 中断使能寄存器 (Interrupt Enable Register)
#define UART_FCR        0x02    // FIFO控制寄存器 (FIFO Control Register)
#define UART_IIR        0x02    // 中断标识寄存器 (Interrupt Identification Register)
#define UART_LCR        0x03    // 线路控制寄存器 (Line Control Register)
#define UART_MCR        0x04    // 调制解调器控制寄存器 (Modem Control Register)
#define UART_LSR        0x05    // 线路状态寄存器 (Line Status Register)
#define UART_MSR        0x06    // 调制解调器状态寄存器 (Modem Status Register)
#define UART_SCR        0x07    // 暂存寄存器 (Scratch Register)

// 除数锁存器 (当LCR.DLAB=1时)
#define UART_DLL        0x00    // 除数锁存器低位 (Divisor Latch Low)
#define UART_DLM        0x01    // 除数锁存器高位 (Divisor Latch High)

// 线路状态寄存器 (LSR) 位定义
#define UART_LSR_DR     0x01    // 数据准备就绪 (Data Ready)
#define UART_LSR_OE     0x02    // 溢出错误 (Overrun Error)
#define UART_LSR_PE     0x04    // 奇偶校验错误 (Parity Error)
#define UART_LSR_FE     0x08    // 帧错误 (Framing Error)
#define UART_LSR_BI     0x10    // 中断指示 (Break Interrupt)
#define UART_LSR_THRE   0x20    // 发送保持寄存器空 (Transmit Holding Register Empty)
#define UART_LSR_TEMT   0x40    // 发送器空 (Transmitter Empty)
#define UART_LSR_FIFOE  0x80    // FIFO错误 (FIFO Error)

// 线路控制寄存器 (LCR) 位定义
#define UART_LCR_WLS0   0x01    // 字长选择位0
#define UART_LCR_WLS1   0x02    // 字长选择位1
#define UART_LCR_STB    0x04    // 停止位数量 (0=1位, 1=1.5或2位)
#define UART_LCR_PEN    0x08    // 奇偶校验使能
#define UART_LCR_EPS    0x10    // 偶校验选择
#define UART_LCR_SP     0x20    // 粘滞奇偶校验
#define UART_LCR_BC     0x40    // 中断控制
#define UART_LCR_DLAB   0x80    // 除数锁存器访问位

// 数据位长度定义
#define UART_LCR_8BIT   (UART_LCR_WLS1 | UART_LCR_WLS0)  // 8数据位
#define UART_LCR_7BIT   (UART_LCR_WLS1)                  // 7数据位
#define UART_LCR_6BIT   (UART_LCR_WLS0)                  // 6数据位
#define UART_LCR_5BIT   (0)                              // 5数据位

// FIFO控制寄存器 (FCR) 位定义
#define UART_FCR_FE     0x01    // FIFO使能
#define UART_FCR_RFR    0x02    // 接收FIFO复位
#define UART_FCR_TFR    0x04    // 发送FIFO复位
#define UART_FCR_DMS    0x08    // DMA模式选择
#define UART_FCR_RTL0   0x40    // 接收触发级别位0
#define UART_FCR_RTL1   0x80    // 接收触发级别位1

// 常用波特率除数 (假设时钟频率为1.8432MHz)
#define UART_BAUD_115200    1
#define UART_BAUD_57600     2
#define UART_BAUD_38400     3
#define UART_BAUD_19200     6
#define UART_BAUD_9600      12

// UART寄存器读写宏
#define UART_REG(offset)    ((volatile uint8_t*)(UART_BASE + (offset)))
#define uart_read(offset)   (*UART_REG(offset))
#define uart_write(offset, value) (*UART_REG(offset) = (value))

// UART操作函数声明
void uart_init(void);
void uart_putc(char c);
char uart_getc(void);
int uart_puts(const char *s);
int uart_tx_ready(void);
int uart_rx_ready(void);

// 内联函数实现
static inline void uart_wait_tx_ready(void)
{
    // 等待发送保持寄存器空
    while (!(uart_read(UART_LSR) & UART_LSR_THRE)) {
        // 忙等待
    }
}

static inline void uart_wait_tx_empty(void)
{
    // 等待发送器完全空
    while (!(uart_read(UART_LSR) & UART_LSR_TEMT)) {
        // 忙等待
    }
}

#endif /* __UART_H */ 