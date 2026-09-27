# ARM32-BIT CPU — RTL Design (Verilog + SystemVerilog)

---

## Project Overview
This repository contains a complete **ARM32-bit CPU** designed using **Verilog/SystemVerilog** and verified using **Vivado 2025.1** and **EDAPlayground**.  
The CPU follows a simplified educational ARM architecture (from *Harris & Harris: Digital Design and Computer Architecture — ARM Edition*), implementing:

- 32-bit datapath  
- Instruction Fetch → Decode → Execute flow  
- ARM flags (N, Z, C, V)  
- ALU operations — ADD, SUB, AND, OR  
- Conditional execution  
- Register file (R0–R15 with PC+8 behavior)  
- IMEM (instruction memory)  
- DMEM (data memory)  
- Complete CPU integration with a testbench  

All RTL modules are complete, functional, and verified.

---



---

## Module Details

### **ALU — Arithmetic Logic Unit**
- Functions: ADD, SUB, AND, OR  
- Inputs: `SrcA[31:0]`, `SrcB[31:0]`, `ALUControl[1:0]`  
- Outputs: `ALUResult[31:0]`, `ALUFlags[3:0]`  
- Flags generated:  
  - N (Negative)  
  - Z (Zero)  
  - C (Carry)  
  - V (Overflow)  
- Verified in EDAPlayground & Vivado  

---

### **Datapath**
Includes:
- Program Counter (PC)
- PC increment logic (PC → PC+4 → PC+8)
- Register File (R0–R15)
- ALU
- Immediate Extender
- MUX structures
- Write-back path

**Status:** Verified and stable.

---

### **Controller**
Contains:
- Main decoder  
- ALU decoder  
- Conditional execution logic  

Generates:
- RegWrite  
- MemWrite  
- ImmSrc  
- ALUSrc  
- FlagW  
- MemtoReg  
- PCSrc  
- RegSrc  

**Status:** Verified.

---

### **Instruction Memory (IMEM)**
- 64 × 32-bit  

- Works correctly in EDAPlayground  
- Vivado requires correct file placement 

---

### **Data Memory (DMEM)**
- 64 × 32-bit RAM  
- Write-enable controlled by `MemWrite`  
- Verified.

---

### **Top-Level CPU**
Connects:
- Datapath  
- Controller  
- IMEM  
- DMEM  

Status: Fully functional CPU simulation achieved.

---

## CPU Architecture (Images to Upload on GitHub Later)

### Datapath Diagram  
<img width="1016" height="693" alt="Screenshot 2025-11-24 130530" src="https://github.com/user-attachments/assets/5457852c-b883-4222-80a8-0b2233f0df48" />


### RTL Architecture  
<img width="1563" height="698" alt="Screenshot 2025-11-24 130320" src="https://github.com/user-attachments/assets/98c7dd41-5c3c-4398-b52e-3a695c05dd43" />


---

## Compliance Checklist

| Feature / Requirement | Status | Notes |
|----------------------|:------:|-------|
| 32-bit ALU | Pass | ADD/SUB/AND/OR |
| ARM Flags N,Z,C,V | Pass | Matches ARM behavior |
| Register File | Pass | R15 = PC+8 |
| Datapath | Pass | Verified |
| Instruction Memory | Pass | Loads from memfile.dat |
| Data Memory | Pass | Read/Write OK |
| EDAPlayground CPU Run | Pass | Fully successful |
| Vivado Compatibility | InProgress | memfile.dat must be placed manually |
| Testbench | Pass | Clock/Reset + CPU integration |

---

## Directory Structure

```
ARM32_BIT_CPU/
│── adder.v
│── alu.v
│── condlogic.v
│── condcheck.v
│── controller.v
│── cpu.v
│── datapath.v
│── decoder.v
│── dmem.v
│── extend.v
│── flopr.v
│── flopenr.v
│── imem.v
│── memfile.dat
│── mux2.v
│── regfile.v
│── testbench.sv
│── top.v
└── README.md
```

---

## Simulation Instructions

###  Full CPU Simulation (EDAPlayground)  
https://www.edaplayground.com/x/Hk54

###  Waveform Viewer (EPWave)  
https://www.edaplayground.com/launchEpwave

---

## Vivado Simulation (Windows)

###  Important  
Vivado does **not** automatically detect memfile.dat.  
You must place it manually here:

```
PROJECT_NAME.srcs/sim_1/imports/memfile.dat
```
---

## Project Status

-  All RTL modules implemented  
-  Full CPU simulation successful on EDAPlayground  
-  ALU and Datapath verified on Vivado  
-  Register file, memory, decoder, controller verified  
-  Suitable for portfolio, resume, and interviews  
-  Vivado requires proper memfile.dat placement  

---

## Results

### Edaplayground Simulation Result
<img width="1913" height="415" alt="image" src="https://github.com/user-attachments/assets/cec2a436-224a-4a70-88ff-80a526673a41" />


### Vivado ALU Waveform  
<img width="1915" height="987" alt="Screenshot 2025-11-24 124904" src="https://github.com/user-attachments/assets/51791160-d780-44f0-ad7e-9beaf3e080af" />


---
## License
Released under the **MIT License**.

---

## Acknowledgments

- This project is derived from the educational ARM architecture presented in **Digital Design and Computer Architecture — ARM Edition** (Harris & Harris).  
- Verified using **Vivado**, **Icarus Verilog**, and **EDAPlayground**.  
---

